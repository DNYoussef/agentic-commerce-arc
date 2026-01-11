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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from database import init_db, close_db, get_db
from auth import get_jwt_auth, get_current_user, TokenResponse, UserCreate, UserLogin
from agent import CommerceAgent
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

@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """
    WebSocket endpoint for streaming chat.

    Message format (incoming):
    {
        "type": "chat" | "search" | "generate",
        "content": "message content",
        "context": {...}  // optional
    }

    Message format (outgoing):
    {
        "type": "chunk" | "complete" | "error" | "action",
        "content": "...",
        "metadata": {...}
    }
    """
    user_id = None

    try:
        # Accept connection
        await ws_manager.connect(websocket, connection_id)

        # Wait for authentication message
        auth_data = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=30.0
        )

        if auth_data.get("type") != "auth":
            await websocket.send_json({
                "type": "error",
                "content": "First message must be authentication"
            })
            return

        # Verify token
        jwt_auth = get_jwt_auth()
        token = auth_data.get("token", "")
        payload = jwt_auth.verify_token(token, token_type="access")

        if not payload:
            await websocket.send_json({
                "type": "error",
                "content": "Invalid or expired token"
            })
            return

        user_id = payload.get("sub")

        # Send auth success
        await websocket.send_json({
            "type": "auth_success",
            "content": "Authentication successful"
        })

        # Main message loop
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "chat")
            content = data.get("content", "")
            context = data.get("context", {})

            if msg_type == "chat":
                # Stream chat response
                async for chunk in commerce_agent.stream_response(
                    message=content,
                    user_id=user_id,
                    context=context,
                ):
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk["content"],
                        "metadata": chunk.get("metadata", {}),
                    })

                # Send completion
                await websocket.send_json({
                    "type": "complete",
                    "content": "",
                })

            elif msg_type == "search":
                # Product search
                results = await commerce_agent.search_products(
                    query=content,
                    category=context.get("category"),
                )
                await websocket.send_json({
                    "type": "search_results",
                    "content": results,
                })

            elif msg_type == "generate":
                # Image generation
                result = await commerce_agent.generate_product_image(
                    prompt=content,
                    style=context.get("style", "product"),
                )
                await websocket.send_json({
                    "type": "image_result",
                    "content": result,
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket {connection_id} disconnected")
    except asyncio.TimeoutError:
        logger.warning(f"WebSocket {connection_id} auth timeout")
        await websocket.close(code=4001, reason="Authentication timeout")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": str(e),
            })
        except:
            pass
    finally:
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
