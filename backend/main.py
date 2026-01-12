"""
Agentic Commerce on Arc - FastAPI Backend

Production-ready FastAPI application with WebSocket streaming for AI chat,
JWT authentication, and integration with Replicate for image generation.

Based on library components:
- realtime/websocket_manager (92% match)
- security/jwt_auth (88% match)
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from web3 import Web3

from database import (
    init_db,
    close_db,
    get_db,
    create_transaction,
    get_transaction_by_hash,
    get_transaction_by_idempotency_key,
    update_transaction_status,
)
from auth import get_current_user, TokenResponse, UserCreate, UserLogin
from agent import CommerceAgent
from blockchain import verify_escrow_transaction
from models.schemas import (
    ProductSearch,
    ProductResponse,
    ImageGenerationRequest,
    ImageGenerationResponse,
    ChatMessage,
    ChatResponse,
    PriceComparisonRequest,
    PriceComparisonResponse,
    HealthResponse,
    TransactionVerifyRequest,
    TransactionVerifyResponse,
    TransactionStatus,
    TransactionType,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# WebSocket connection manager (adapted from library)
class ConnectionManager:
    """WebSocket connection manager with room support."""

    def __init__(self):
        self._connections: Dict[str, WebSocket] = {}
        self._user_connections: Dict[str, set] = {}
        self._lock = asyncio.Lock()

    @property
    def active_connections(self) -> int:
        return len(self._connections)

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: Optional[str] = None,
    ):
        """Accept and register a WebSocket connection."""
        await websocket.accept()

        async with self._lock:
            self._connections[connection_id] = websocket

            if user_id:
                if user_id not in self._user_connections:
                    self._user_connections[user_id] = set()
                self._user_connections[user_id].add(connection_id)

        logger.info(f"WebSocket connected: {connection_id}, user={user_id}")

    def disconnect(self, connection_id: str, user_id: Optional[str] = None):
        """Remove a WebSocket connection."""
        self._connections.pop(connection_id, None)

        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(connection_id)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_personal(self, connection_id: str, message: dict):
        """Send message to a specific connection."""
        websocket = self._connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                self.disconnect(connection_id)

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a user."""
        connection_ids = self._user_connections.get(user_id, set())
        for conn_id in connection_ids:
            await self.send_personal(conn_id, message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        for conn_id in list(self._connections.keys()):
            await self.send_personal(conn_id, message)


# Global instances
ws_manager = ConnectionManager()
commerce_agent: Optional[CommerceAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global commerce_agent

    # Startup
    logger.info("Starting Agentic Commerce backend...")
    await init_db()
    commerce_agent = CommerceAgent()
    await commerce_agent.initialize()
    logger.info("Backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down backend...")
    await close_db()
    if commerce_agent:
        await commerce_agent.shutdown()
    logger.info("Backend shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Agentic Commerce on Arc",
    description="AI-powered shopping assistant with blockchain integration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Health Check Endpoints
# ==============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for Railway deployment."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "database": "connected",
            "websocket": f"{ws_manager.active_connections} connections",
            "agent": "ready" if commerce_agent else "not_initialized",
        }
    )


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "name": "Agentic Commerce on Arc",
        "status": "running",
        "docs": "/docs",
    }


# ==============================================================================
# Authentication Endpoints
# ==============================================================================

@app.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
async def register(user_data: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    from auth import register_user
    return await register_user(user_data, db)


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    """Login and get access token."""
    from auth import authenticate_user
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    return await authenticate_user(user_login, db)


@app.post("/auth/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(refresh_token: str, db=Depends(get_db)):
    """Refresh access token."""
    from auth import refresh_access_token
    return await refresh_access_token(refresh_token, db)


# ==============================================================================
# Chat/Agent Endpoints
# ==============================================================================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Process a chat message through the AI agent."""
    if not commerce_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    response = await commerce_agent.process_message(
        message=message.content,
        user_id=current_user["sub"],
        context=message.context,
    )

    return ChatResponse(
        message=response["message"],
        actions=response.get("actions", []),
        products=response.get("products", []),
        images=response.get("images", []),
    )


# ==============================================================================
# Product Endpoints
# ==============================================================================

@app.post("/products/search", response_model=list[ProductResponse], tags=["Products"])
async def search_products(
    search: ProductSearch,
    current_user: dict = Depends(get_current_user),
):
    """Search for products."""
    if not commerce_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    results = await commerce_agent.search_products(
        query=search.query,
        category=search.category,
        max_price=search.max_price,
        min_price=search.min_price,
    )

    return [ProductResponse(**p) for p in results]


@app.post("/products/compare", response_model=PriceComparisonResponse, tags=["Products"])
async def compare_prices(
    request: PriceComparisonRequest,
    current_user: dict = Depends(get_current_user),
):
    """Compare prices across multiple sources."""
    if not commerce_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    comparison = await commerce_agent.compare_prices(request.product_id)
    return PriceComparisonResponse(**comparison)


# ==============================================================================
# Transaction Endpoints
# ==============================================================================

@app.post("/transactions/verify", response_model=TransactionVerifyResponse, tags=["Transactions"])
async def verify_transaction(
    payload: TransactionVerifyRequest,
    current_user: dict = Depends(get_current_user),
):
    """Verify a transaction on-chain and store it with idempotency safeguards."""
    user_id = int(current_user.get("sub"))

    if payload.idempotency_key:
        existing = await get_transaction_by_idempotency_key(payload.idempotency_key)
        if existing:
            if existing.get("tx_hash") != payload.tx_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key already used with different transaction."
                )
            return TransactionVerifyResponse(
                tx_hash=existing["tx_hash"],
                status=TransactionStatus(existing["status"]),
                verified=existing["status"] == TransactionStatus.CONFIRMED.value,
                amount=existing.get("amount"),
            )

    existing_tx = await get_transaction_by_hash(payload.tx_hash)
    if existing_tx:
        return TransactionVerifyResponse(
            tx_hash=existing_tx["tx_hash"],
            status=TransactionStatus(existing_tx["status"]),
            verified=existing_tx["status"] == TransactionStatus.CONFIRMED.value,
            amount=existing_tx.get("amount"),
        )

    escrow_address = payload.escrow_address or os.getenv("ESCROW_CONTRACT")
    if not escrow_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Escrow contract address is required."
        )

    expected_amount = None
    if payload.amount is not None:
        expected_amount = Web3.to_wei(payload.amount, "ether")

    verification = verify_escrow_transaction(
        tx_hash=payload.tx_hash,
        escrow_address=escrow_address,
        expected_buyer=payload.buyer,
        expected_seller=payload.seller,
        expected_amount=expected_amount,
    )

    status_value = verification.get("status", "pending")
    metadata = json.dumps(
        {
            "verification": verification,
            "product_id": payload.product_id,
        }
    )

    await create_transaction(
        user_id=user_id,
        tx_hash=payload.tx_hash,
        tx_type=TransactionType.PURCHASE.value,
        status=status_value,
        amount=payload.amount,
        idempotency_key=payload.idempotency_key,
        metadata=metadata,
    )

    if status_value in {"confirmed", "failed"}:
        await update_transaction_status(payload.tx_hash, status_value, metadata=metadata)

    return TransactionVerifyResponse(
        tx_hash=payload.tx_hash,
        status=TransactionStatus(status_value),
        verified=verification.get("verified", False),
        escrow_id=verification.get("escrow_id"),
        buyer=verification.get("buyer"),
        seller=verification.get("seller"),
        amount=payload.amount,
        reason=verification.get("reason"),
    )


# ==============================================================================
# Image Generation Endpoints
# ==============================================================================

@app.post("/images/generate", response_model=ImageGenerationResponse, tags=["Images"])
async def generate_image(
    request: ImageGenerationRequest,
    current_user: dict = Depends(get_current_user),
):
    """Generate product image using Replicate."""
    if not commerce_agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )

    result = await commerce_agent.generate_product_image(
        prompt=request.prompt,
        style=request.style,
        aspect_ratio=request.aspect_ratio,
    )

    return ImageGenerationResponse(**result)


# ==============================================================================
# WebSocket Endpoint for Streaming Chat
# ==============================================================================

async def _send_ws(websocket: WebSocket, message: Dict[str, Any]) -> None:
    """Send a JSON message over WebSocket."""
    await websocket.send_json(message)


async def _stream_agent_response(
    websocket: WebSocket,
    user_id: str,
    content: str,
    context: Dict[str, Any],
) -> None:
    """Stream agent responses and tool usage over WebSocket."""
    if not commerce_agent:
        await _send_ws(websocket, {
            "type": "error",
            "message": "Agent not initialized",
        })
        return

    full_response: list[str] = []

    async for chunk in commerce_agent.stream_response(
        message=content,
        user_id=user_id,
        context=context,
    ):
        metadata = chunk.get("metadata", {})
        chunk_type = metadata.get("type", "text")

        if chunk_type == "tool_start":
            await _send_ws(websocket, {
                "type": "tool_start",
                "tool": metadata.get("tool"),
                "args": metadata.get("args"),
            })
            continue

        if chunk_type == "tool_result":
            await _emit_tool_payloads(websocket, metadata)
            continue

        text = chunk.get("content", "")
        if text:
            full_response.append(text)
            await _send_ws(websocket, {
                "type": "text",
                "content": text,
            })

    await _send_ws(websocket, {
        "type": "done",
        "message": "".join(full_response),
    })


async def _emit_tool_payloads(websocket: WebSocket, metadata: Dict[str, Any]) -> None:
    """Send tool result payloads to the client."""
    await _send_ws(websocket, {
        "type": "tool_result",
        "tool": metadata.get("tool"),
        "result": metadata.get("result"),
    })
    if metadata.get("products"):
        await _send_ws(websocket, {
            "type": "products",
            "data": metadata.get("products"),
        })
    if metadata.get("image"):
        await _send_ws(websocket, {
            "type": "image",
            "data": metadata.get("image"),
        })


async def _heartbeat(websocket: WebSocket, interval: int = 20) -> None:
    """Send periodic ping messages to keep the connection alive."""
    while True:
        await asyncio.sleep(interval)
        await _send_ws(websocket, {"type": "ping"})


@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for streaming chat.

    Message format (incoming):
    {"type": "message", "content": "user message here"}

    Message format (outgoing):
    {"type": "text", "content": "streaming text chunk"}
    {"type": "tool_start", "tool": "search_products", "args": {...}}
    {"type": "tool_result", "tool": "search_products", "result": {...}}
    {"type": "products", "data": [...]}
    {"type": "image", "data": {"url": "...", "prompt": "..."}}
    {"type": "error", "message": "error description"}
    {"type": "done", "message": "full response"}
    """
    connection_id = websocket.query_params.get("connection_id") or str(uuid4())
    heartbeat_task: Optional[asyncio.Task] = None

    try:
        await ws_manager.connect(websocket, connection_id, user_id)
        heartbeat_task = asyncio.create_task(_heartbeat(websocket))

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")
            content = data.get("content", "")
            context = data.get("context", {})

            if msg_type == "ping":
                await _send_ws(websocket, {"type": "pong"})
                continue

            if msg_type == "pong":
                continue

            if msg_type == "init":
                continue

            if msg_type != "message":
                await _send_ws(websocket, {
                    "type": "error",
                    "message": "Unsupported message type",
                })
                continue

            await _stream_agent_response(websocket, user_id, content, context)

    except WebSocketDisconnect:
        logger.info(f"WebSocket {connection_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await _send_ws(websocket, {
                "type": "error",
                "message": str(e),
            })
        except:
            pass
    finally:
        if heartbeat_task:
            heartbeat_task.cancel()
        ws_manager.disconnect(connection_id, user_id)


# ==============================================================================
# Run with Uvicorn (for local development)
# ==============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "development") == "development",
    )
