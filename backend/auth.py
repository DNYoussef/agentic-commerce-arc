"""
Authentication Module - JWT-based authentication for Agentic Commerce.

Adapted from library component: components/security/jwt_auth
Implements OWASP API2:2023 Broken Authentication mitigations.

Features:
- JWT access/refresh token management
- Bcrypt password hashing
- FastAPI OAuth2 integration
- Token refresh flow
"""

import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from database import get_user_by_email, get_user_by_id, create_user

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =============================================================================
# Pydantic Models
# =============================================================================

class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str
    wallet_address: Optional[str] = None


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response for login/register."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User data response."""
    id: int
    email: str
    wallet_address: Optional[str]
    created_at: str


# =============================================================================
# JWT Authentication Class (adapted from library)
# =============================================================================

@dataclass
class JWTConfig:
    """JWT configuration."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: Optional[str] = None
    audience: Optional[str] = None


class JWTAuth:
    """
    JWT Authentication Manager.

    Provides JWT token management and password hashing.
    Adapted from library component for this project.
    """

    MIN_SECRET_KEY_LENGTH = 32

    def __init__(self, config: JWTConfig):
        self._config = config
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Validate secret key length
        if len(self._config.secret_key) < self.MIN_SECRET_KEY_LENGTH:
            logger.warning(
                f"Secret key shorter than recommended {self.MIN_SECRET_KEY_LENGTH} bytes. "
                "Consider using a longer key for production."
            )

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self._pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self._pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self,
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self._config.access_token_expire_minutes
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })

        if self._config.issuer:
            to_encode["iss"] = self._config.issuer
        if self._config.audience:
            to_encode["aud"] = self._config.audience

        return jwt.encode(
            to_encode,
            self._config.secret_key,
            algorithm=self._config.algorithm
        )

    def create_refresh_token(
        self,
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self._config.refresh_token_expire_days
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)
        })

        if self._config.issuer:
            to_encode["iss"] = self._config.issuer
        if self._config.audience:
            to_encode["aud"] = self._config.audience

        return jwt.encode(
            to_encode,
            self._config.secret_key,
            algorithm=self._config.algorithm
        )

    def verify_token(
        self,
        token: str,
        token_type: str = "access"
    ) -> Optional[dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self._config.secret_key,
                algorithms=[self._config.algorithm],
                audience=self._config.audience if self._config.audience else None,
                issuer=self._config.issuer if self._config.issuer else None,
                options={
                    "verify_iss": bool(self._config.issuer),
                    "verify_aud": bool(self._config.audience)
                }
            )

            # Verify token type
            if payload.get("type") != token_type:
                return None

            return payload

        except JWTError as e:
            logger.debug(f"Token verification failed: {e}")
            return None

    def get_subject_from_token(
        self,
        token: str,
        token_type: str = "access"
    ) -> Optional[str]:
        """Extract subject from a verified token."""
        payload = self.verify_token(token, token_type=token_type)
        if not payload:
            return None
        sub = payload.get("sub")
        return str(sub) if sub is not None else None

    @property
    def config(self) -> JWTConfig:
        """Get current configuration."""
        return self._config


# =============================================================================
# Global JWT Auth Instance
# =============================================================================

_jwt_auth: Optional[JWTAuth] = None


def get_jwt_auth() -> JWTAuth:
    """Get the global JWT auth instance."""
    global _jwt_auth
    if _jwt_auth is None:
        _jwt_auth = JWTAuth(JWTConfig(
            secret_key=SECRET_KEY,
            algorithm=ALGORITHM,
            access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=REFRESH_TOKEN_EXPIRE_DAYS,
            issuer="agentic-commerce",
            audience="agentic-commerce-api",
        ))
    return _jwt_auth


# =============================================================================
# Authentication Functions
# =============================================================================

async def register_user(user_data: UserCreate, db) -> TokenResponse:
    """Register a new user."""
    jwt_auth = get_jwt_auth()

    # Check if user exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password and create user
    hashed_password = jwt_auth.hash_password(user_data.password)
    user_id = await create_user(
        email=user_data.email,
        hashed_password=hashed_password,
        wallet_address=user_data.wallet_address
    )

    # Create tokens
    token_data = {"sub": str(user_id), "email": user_data.email}
    access_token = jwt_auth.create_access_token(token_data)
    refresh_token = jwt_auth.create_refresh_token(token_data)

    logger.info(f"User registered: {user_data.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


async def authenticate_user(user_login: UserLogin, db) -> TokenResponse:
    """Authenticate a user and return tokens."""
    jwt_auth = get_jwt_auth()

    # Get user by email
    user = await get_user_by_email(user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    if not jwt_auth.verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create tokens
    token_data = {"sub": str(user["id"]), "email": user["email"]}
    access_token = jwt_auth.create_access_token(token_data)
    refresh_token = jwt_auth.create_refresh_token(token_data)

    logger.info(f"User authenticated: {user_login.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


async def refresh_access_token(refresh_token: str, db) -> TokenResponse:
    """Refresh an access token using a refresh token."""
    jwt_auth = get_jwt_auth()

    # Verify refresh token
    payload = jwt_auth.verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Get user to ensure they still exist and are active
    user = await get_user_by_id(int(user_id))
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create new tokens
    token_data = {"sub": str(user["id"]), "email": user["email"]}
    new_access_token = jwt_auth.create_access_token(token_data)
    new_refresh_token = jwt_auth.create_refresh_token(token_data)

    logger.info(f"Token refreshed for user: {user['email']}")

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get the current authenticated user from the JWT token.

    FastAPI dependency for protected endpoints.
    """
    jwt_auth = get_jwt_auth()

    payload = jwt_auth.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Return the payload (contains sub, email, etc.)
    return payload


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[dict]:
    """
    Optionally get the current user (for endpoints that work with or without auth).
    """
    if not token:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None


# =============================================================================
# Utility Functions
# =============================================================================

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_api_key(prefix: str = "sk") -> str:
    """Generate an API key with prefix."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"
