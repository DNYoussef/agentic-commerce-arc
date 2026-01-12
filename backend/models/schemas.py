"""
Pydantic Schemas - Request/Response models for Agentic Commerce API.

Adapted from library component: components/api/pydantic_base_models
Provides type-safe API contracts with validation.

Features:
- Request validation
- Response serialization
- OpenAPI documentation
- Type safety
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# =============================================================================
# Health Check
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status", examples=["healthy"])
    version: str = Field(..., description="API version", examples=["1.0.0"])
    timestamp: str = Field(..., description="Current server time")
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of dependent services"
    )


# =============================================================================
# Product Schemas
# =============================================================================

class ProductSearch(BaseModel):
    """Product search request."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query",
        examples=["wireless headphones"]
    )
    category: Optional[str] = Field(
        None,
        description="Product category filter",
        examples=["electronics"]
    )
    min_price: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum price filter"
    )
    max_price: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum price filter"
    )
    sort_by: Optional[str] = Field(
        "relevance",
        description="Sort order",
        examples=["relevance", "price_asc", "price_desc", "rating"]
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum results to return"
    )


class ProductResponse(BaseModel):
    """Product details response."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Product identifier")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Product price")
    currency: str = Field("USD", description="Price currency")
    category: Optional[str] = Field(None, description="Product category")
    image_url: Optional[str] = Field(None, description="Product image URL")
    source: str = Field(..., description="Data source")
    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Average rating (0-5)"
    )
    reviews_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of reviews"
    )
    in_stock: bool = Field(True, description="Availability status")
    url: Optional[str] = Field(None, description="Product page URL")


# =============================================================================
# Price Comparison Schemas
# =============================================================================

class PriceComparisonRequest(BaseModel):
    """Price comparison request."""
    product_id: str = Field(
        ...,
        description="Product identifier to compare",
        examples=["prod_001"]
    )
    include_shipping: bool = Field(
        True,
        description="Include shipping costs in comparison"
    )


class PriceSourceResult(BaseModel):
    """Price from a single source."""
    source: str = Field(..., description="Retailer name")
    price: float = Field(..., ge=0, description="Product price")
    currency: str = Field("USD", description="Price currency")
    url: Optional[str] = Field(None, description="Product page URL")
    in_stock: bool = Field(True, description="Availability")
    shipping: Optional[float] = Field(None, ge=0, description="Shipping cost")
    total: float = Field(..., ge=0, description="Total price with shipping")


class BestDeal(BaseModel):
    """Best deal information."""
    source: str = Field(..., description="Retailer with best price")
    price: float = Field(..., ge=0, description="Best price")
    shipping: Optional[float] = Field(None, description="Shipping cost")
    total: float = Field(..., ge=0, description="Total price")
    currency: str = Field("USD", description="Currency")
    url: Optional[str] = Field(None, description="Product URL")
    in_stock: bool = Field(True, description="Availability")
    savings: float = Field(0, description="Savings vs average")
    savings_percent: float = Field(0, description="Savings percentage")


class PriceComparisonResponse(BaseModel):
    """Price comparison response."""
    product_name: str = Field(..., description="Product name")
    product_id: Optional[str] = Field(None, description="Product identifier")
    sources: List[PriceSourceResult] = Field(
        default_factory=list,
        description="Prices from all sources"
    )
    best_deal: Optional[BestDeal] = Field(
        None,
        description="Best deal information"
    )
    fetched_at: str = Field(..., description="When prices were fetched")
    cached: bool = Field(False, description="Whether result was cached")


# =============================================================================
# Image Generation Schemas
# =============================================================================

class ImageStyle(str, Enum):
    """Available image styles."""
    PRODUCT = "product"
    LIFESTYLE = "lifestyle"
    MINIMALIST = "minimalist"
    ARTISTIC = "artistic"


class AspectRatio(str, Enum):
    """Available aspect ratios."""
    SQUARE = "1:1"
    WIDE = "16:9"
    PORTRAIT = "9:16"
    STANDARD = "4:3"
    TALL = "3:4"


class ImageGenerationRequest(BaseModel):
    """Image generation request."""
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Image description",
        examples=["A sleek wireless headphone with noise cancellation"]
    )
    style: ImageStyle = Field(
        ImageStyle.PRODUCT,
        description="Image style preset"
    )
    aspect_ratio: AspectRatio = Field(
        AspectRatio.SQUARE,
        description="Image aspect ratio"
    )


class ImageGenerationResponse(BaseModel):
    """Image generation response."""
    image_url: str = Field(..., description="Generated image URL")
    prompt: str = Field(..., description="Original prompt")
    style: str = Field(..., description="Applied style")
    model: str = Field(..., description="Model used for generation")
    prediction_id: Optional[str] = Field(
        None,
        description="Replicate prediction ID"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


# =============================================================================
# Chat Schemas
# =============================================================================

class ChatMessage(BaseModel):
    """Chat message from user."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message content",
        examples=["Find me wireless headphones under $100"]
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context"
    )


class ActionType(str, Enum):
    """Types of actions the agent can take."""
    SEARCH = "search"
    GENERATE_IMAGE = "generate_image"
    COMPARE_PRICES = "compare_prices"
    RECOMMEND = "recommend"
    BLOCKCHAIN = "blockchain"


class ChatAction(BaseModel):
    """Action taken by the agent."""
    type: ActionType = Field(..., description="Action type")
    query: Optional[str] = Field(None, description="Search query if applicable")
    prompt: Optional[str] = Field(None, description="Image prompt if applicable")
    product: Optional[str] = Field(None, description="Product if applicable")
    result: Optional[Dict[str, Any]] = Field(None, description="Action result")


class ChatResponse(BaseModel):
    """Chat response from agent."""
    message: str = Field(..., description="Agent's response message")
    actions: List[ChatAction] = Field(
        default_factory=list,
        description="Actions taken by agent"
    )
    products: List[ProductResponse] = Field(
        default_factory=list,
        description="Products found"
    )
    images: List[ImageGenerationResponse] = Field(
        default_factory=list,
        description="Images generated"
    )


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email address")
    wallet_address: Optional[str] = Field(
        None,
        description="Blockchain wallet address"
    )


class UserCreate(UserBase):
    """User creation request."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)"
    )


class UserResponse(UserBase):
    """User response (no password)."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Account creation time")
    is_active: bool = Field(True, description="Account status")


# =============================================================================
# WebSocket Message Schemas
# =============================================================================

class WSMessageType(str, Enum):
    """WebSocket message types."""
    AUTH = "auth"
    CHAT = "chat"
    SEARCH = "search"
    GENERATE = "generate"
    PING = "ping"
    PONG = "pong"
    CHUNK = "chunk"
    COMPLETE = "complete"
    ERROR = "error"
    AUTH_SUCCESS = "auth_success"
    SEARCH_RESULTS = "search_results"
    IMAGE_RESULT = "image_result"


class WSIncomingMessage(BaseModel):
    """Incoming WebSocket message."""
    type: WSMessageType = Field(..., description="Message type")
    content: Optional[str] = Field(None, description="Message content")
    token: Optional[str] = Field(None, description="Auth token (for auth type)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class WSOutgoingMessage(BaseModel):
    """Outgoing WebSocket message."""
    type: WSMessageType = Field(..., description="Message type")
    content: Any = Field(None, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# =============================================================================
# Transaction Schemas (Blockchain)
# =============================================================================

class TransactionStatus(str, Enum):
    """Transaction status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class TransactionType(str, Enum):
    """Transaction types."""
    PURCHASE = "purchase"
    TRANSFER = "transfer"
    SWAP = "swap"


class TransactionRequest(BaseModel):
    """Transaction request."""
    tx_type: TransactionType = Field(..., description="Transaction type")
    amount: float = Field(..., gt=0, description="Transaction amount")
    token_address: Optional[str] = Field(
        None,
        description="Token contract address"
    )
    recipient: Optional[str] = Field(None, description="Recipient address")
    product_id: Optional[str] = Field(None, description="Product being purchased")


class TransactionResponse(BaseModel):
    """Transaction response."""
    id: int = Field(..., description="Transaction ID")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    tx_type: TransactionType = Field(..., description="Transaction type")
    status: TransactionStatus = Field(..., description="Transaction status")
    amount: float = Field(..., description="Transaction amount")
    created_at: datetime = Field(..., description="Creation time")
    confirmed_at: Optional[datetime] = Field(None, description="Confirmation time")


class TransactionVerifyRequest(BaseModel):
    """Request to verify a transaction on-chain."""
    tx_hash: str = Field(..., description="Transaction hash")
    escrow_address: Optional[str] = Field(None, description="Escrow contract address")
    buyer: Optional[str] = Field(None, description="Expected buyer address")
    seller: Optional[str] = Field(None, description="Expected seller address")
    amount: Optional[float] = Field(None, description="Expected amount in ETH/ARC")
    product_id: Optional[str] = Field(None, description="Product identifier")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key")


class TransactionVerifyResponse(BaseModel):
    """Verification result."""
    tx_hash: str = Field(..., description="Transaction hash")
    status: TransactionStatus = Field(..., description="Transaction status")
    verified: bool = Field(..., description="Whether verification succeeded")
    escrow_id: Optional[str] = Field(None, description="Escrow ID")
    buyer: Optional[str] = Field(None, description="Buyer address")
    seller: Optional[str] = Field(None, description="Seller address")
    amount: Optional[float] = Field(None, description="Escrow amount")
    reason: Optional[str] = Field(None, description="Failure reason if any")
