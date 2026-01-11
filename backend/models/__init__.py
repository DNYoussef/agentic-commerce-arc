"""
Models package for Agentic Commerce.

Provides Pydantic schemas for API request/response validation.
"""

from .schemas import (
    # Health
    HealthResponse,
    # Products
    ProductSearch,
    ProductResponse,
    PriceComparisonRequest,
    PriceComparisonResponse,
    PriceSourceResult,
    # Images
    ImageGenerationRequest,
    ImageGenerationResponse,
    # Chat
    ChatMessage,
    ChatResponse,
    ChatAction,
    # User
    UserBase,
    UserCreate,
    UserResponse,
)

__all__ = [
    "HealthResponse",
    "ProductSearch",
    "ProductResponse",
    "PriceComparisonRequest",
    "PriceComparisonResponse",
    "PriceSourceResult",
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "ChatMessage",
    "ChatResponse",
    "ChatAction",
    "UserBase",
    "UserCreate",
    "UserResponse",
]
