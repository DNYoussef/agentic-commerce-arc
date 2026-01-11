"""
Replicate API Client - AI image generation with circuit breaker protection.

Adapted from library component: components/trading/circuit_breakers
Implements circuit breaker pattern to protect against API failures.

Features:
- Automatic failure detection and recovery
- Exponential backoff on failures
- Thread-safe state management
- Comprehensive metrics tracking
"""

import asyncio
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Replicate API configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_BASE_URL = "https://api.replicate.com/v1"

# Default model for image generation (Flux)
DEFAULT_MODEL = "black-forest-labs/flux-schnell"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    failure_rate_threshold: float = 0.5
    success_threshold: int = 3
    failure_window_seconds: int = 60
    open_timeout_seconds: int = 60
    half_open_timeout_seconds: int = 30
    exponential_backoff: bool = True
    max_backoff_seconds: int = 300
    backoff_multiplier: float = 2.0
    min_requests_for_rate: int = 10


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_trips: int = 0
    time_in_open_state: float = 0.0
    average_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_trip_time: Optional[datetime] = None
    last_recovery_time: Optional[datetime] = None


@dataclass
class RequestResult:
    """Result of a protected request."""
    success: bool
    response_time: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class CircuitOpenException(Exception):
    """Exception when circuit breaker is open."""
    def __init__(self, breaker_name: str, message: str = None):
        self.breaker_name = breaker_name
        self.message = message or f"Circuit breaker '{breaker_name}' is open"
        super().__init__(self.message)


class CircuitBreaker:
    """
    Circuit breaker implementation for API protection.

    Adapted from library component with simplifications for this use case.
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.state_changed_time = datetime.now()
        self._lock = asyncio.Lock()
        self.metrics = CircuitBreakerMetrics()
        self.request_history: deque = deque(maxlen=1000)
        self.recent_failures: deque = deque()
        self.recent_successes = 0
        self.backoff_count = 0
        self.current_backoff = self.config.open_timeout_seconds

        logger.info(f"Circuit breaker '{name}' initialized")

    async def call(self, protected_function: Callable, *args, **kwargs) -> Any:
        """Execute a function protected by this circuit breaker."""
        start_time = time.time()

        if not await self._can_make_request():
            self.metrics.failed_requests += 1
            raise CircuitOpenException(self.name)

        try:
            if asyncio.iscoroutinefunction(protected_function):
                result = await protected_function(*args, **kwargs)
            else:
                result = protected_function(*args, **kwargs)

            response_time = time.time() - start_time
            await self._record_success(response_time)
            return result

        except CircuitOpenException:
            raise
        except Exception as e:
            response_time = time.time() - start_time
            await self._record_failure(str(e), response_time)
            raise

    async def _can_make_request(self) -> bool:
        """Check if request is allowed."""
        async with self._lock:
            current_time = datetime.now()

            if self.state == CircuitState.CLOSED:
                return True

            elif self.state == CircuitState.OPEN:
                time_since_trip = (current_time - self.state_changed_time).total_seconds()
                if time_since_trip >= self.current_backoff:
                    self._transition_to_half_open()
                    return True
                return False

            elif self.state == CircuitState.HALF_OPEN:
                return True

            return False

    async def _record_success(self, response_time: float):
        """Record successful request."""
        async with self._lock:
            current_time = datetime.now()
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self._update_average_response_time(response_time)

            result = RequestResult(True, response_time, None, current_time)
            self.request_history.append(result)

            if self.state == CircuitState.HALF_OPEN:
                self.recent_successes += 1
                if self.recent_successes >= self.config.success_threshold:
                    self._transition_to_closed()

            elif self.state == CircuitState.CLOSED:
                self._clean_old_failures()

    async def _record_failure(self, error_message: str, response_time: float):
        """Record failed request."""
        async with self._lock:
            current_time = datetime.now()
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_failure_time = current_time

            result = RequestResult(False, response_time, error_message, current_time)
            self.request_history.append(result)
            self.recent_failures.append(current_time)

            self._clean_old_failures()

            if self._should_trip_circuit():
                await self._trip_circuit()
            elif self.state == CircuitState.HALF_OPEN:
                self._transition_to_open()

    def _update_average_response_time(self, response_time: float):
        """Update rolling average response time."""
        if self.metrics.total_requests == 1:
            self.metrics.average_response_time = response_time
        else:
            alpha = 0.1
            self.metrics.average_response_time = (
                alpha * response_time +
                (1 - alpha) * self.metrics.average_response_time
            )

    def _should_trip_circuit(self) -> bool:
        """Determine if circuit should trip."""
        if self.state != CircuitState.CLOSED:
            return False

        recent_failure_count = len(self.recent_failures)

        # Check failure count threshold
        if recent_failure_count >= self.config.failure_threshold:
            return True

        return False

    async def _trip_circuit(self):
        """Trip the circuit to open state."""
        logger.warning(f"Circuit breaker '{self.name}' tripping to OPEN state")

        self._transition_to_open()
        self.metrics.circuit_trips += 1
        self.metrics.last_trip_time = datetime.now()

        if self.config.exponential_backoff:
            self.current_backoff = min(
                self.config.open_timeout_seconds * (self.config.backoff_multiplier ** self.backoff_count),
                self.config.max_backoff_seconds
            )
            self.backoff_count += 1
        else:
            self.current_backoff = self.config.open_timeout_seconds

    def _transition_to_open(self):
        """Transition to OPEN state."""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.state_changed_time = datetime.now()
            self.recent_successes = 0
            logger.info(f"Circuit breaker '{self.name}' -> OPEN (backoff: {self.current_backoff}s)")

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.state_changed_time = datetime.now()
            self.recent_successes = 0
            logger.info(f"Circuit breaker '{self.name}' -> HALF_OPEN")

    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.state_changed_time = datetime.now()
            self.recent_successes = 0
            self.backoff_count = 0
            self.current_backoff = self.config.open_timeout_seconds
            self.metrics.last_recovery_time = datetime.now()
            logger.info(f"Circuit breaker '{self.name}' -> CLOSED (recovered)")

    def _clean_old_failures(self):
        """Remove failures outside the window."""
        current_time = datetime.now()
        window_start = current_time - timedelta(seconds=self.config.failure_window_seconds)

        while self.recent_failures and self.recent_failures[0] < window_start:
            self.recent_failures.popleft()

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        current_time = datetime.now()
        time_in_state = (current_time - self.state_changed_time).total_seconds()

        failure_rate = (
            self.metrics.failed_requests / self.metrics.total_requests
            if self.metrics.total_requests > 0 else 0.0
        )

        return {
            "name": self.name,
            "state": self.state.value,
            "time_in_current_state_seconds": time_in_state,
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "failure_rate": failure_rate,
            "circuit_trips": self.metrics.circuit_trips,
            "current_backoff_seconds": self.current_backoff,
            "average_response_time": self.metrics.average_response_time,
        }

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED


class ReplicateClient:
    """
    Replicate API client with circuit breaker protection.

    Provides image generation via Replicate's API with automatic
    failure handling and recovery.
    """

    def __init__(self):
        self.api_token = REPLICATE_API_TOKEN
        self.base_url = REPLICATE_BASE_URL
        self.client: Optional[httpx.AsyncClient] = None
        self.circuit_breaker: Optional[CircuitBreaker] = None
        self._initialized = False

    async def initialize(self):
        """Initialize the client."""
        if self._initialized:
            return

        if not self.api_token:
            logger.warning("REPLICATE_API_TOKEN not set - image generation disabled")
            return

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            timeout=120.0  # Long timeout for image generation
        )

        self.circuit_breaker = CircuitBreaker(
            "replicate_api",
            CircuitBreakerConfig(
                failure_threshold=3,
                open_timeout_seconds=30,
                max_backoff_seconds=120
            )
        )

        self._initialized = True
        logger.info("Replicate client initialized")

    async def generate_image(
        self,
        prompt: str,
        style: str = "product",
        aspect_ratio: str = "1:1",
        model: str = DEFAULT_MODEL
    ) -> Dict[str, Any]:
        """
        Generate an image using Replicate.

        Args:
            prompt: Text description of the image
            style: Style preset (product, lifestyle, minimalist, artistic)
            aspect_ratio: Image aspect ratio
            model: Replicate model identifier

        Returns:
            Dict with image_url, prompt, style, model
        """
        if not self._initialized or not self.client:
            logger.warning("Replicate client not initialized, returning mock")
            return {
                "image_url": "https://via.placeholder.com/512",
                "prompt": prompt,
                "style": style,
                "model": "mock",
                "error": "Client not initialized"
            }

        # Enhance prompt based on style
        enhanced_prompt = self._enhance_prompt(prompt, style)

        # Determine dimensions from aspect ratio
        width, height = self._get_dimensions(aspect_ratio)

        try:
            result = await self.circuit_breaker.call(
                self._create_prediction,
                model=model,
                prompt=enhanced_prompt,
                width=width,
                height=height
            )
            return result

        except CircuitOpenException:
            logger.warning("Circuit breaker open - returning fallback")
            return {
                "image_url": "https://via.placeholder.com/512",
                "prompt": prompt,
                "style": style,
                "model": model,
                "error": "Service temporarily unavailable"
            }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "image_url": "https://via.placeholder.com/512",
                "prompt": prompt,
                "style": style,
                "model": model,
                "error": str(e)
            }

    async def _create_prediction(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int
    ) -> Dict[str, Any]:
        """Create a prediction on Replicate."""
        # Create prediction
        response = await self.client.post(
            "/predictions",
            json={
                "version": self._get_model_version(model),
                "input": {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 4,  # Fast for Flux Schnell
                }
            }
        )
        response.raise_for_status()
        prediction = response.json()

        # Poll for completion
        prediction_id = prediction["id"]
        max_attempts = 60
        attempt = 0

        while attempt < max_attempts:
            status_response = await self.client.get(f"/predictions/{prediction_id}")
            status_response.raise_for_status()
            status = status_response.json()

            if status["status"] == "succeeded":
                output = status.get("output", [])
                image_url = output[0] if output else None
                return {
                    "image_url": image_url,
                    "prompt": prompt,
                    "style": "generated",
                    "model": model,
                    "prediction_id": prediction_id
                }

            elif status["status"] == "failed":
                error = status.get("error", "Unknown error")
                raise Exception(f"Prediction failed: {error}")

            elif status["status"] == "canceled":
                raise Exception("Prediction was canceled")

            await asyncio.sleep(1)
            attempt += 1

        raise Exception("Prediction timed out")

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt based on style."""
        style_prefixes = {
            "product": "Professional product photography of",
            "lifestyle": "Lifestyle photography showing",
            "minimalist": "Minimalist, clean composition of",
            "artistic": "Artistic, creative rendering of"
        }

        style_suffixes = {
            "product": ", white background, studio lighting, high resolution, commercial quality",
            "lifestyle": ", natural lighting, real-world setting, authentic feel",
            "minimalist": ", simple background, elegant, modern aesthetic",
            "artistic": ", creative lighting, unique perspective, artistic interpretation"
        }

        prefix = style_prefixes.get(style, "")
        suffix = style_suffixes.get(style, "")

        if prefix:
            return f"{prefix} {prompt}{suffix}"
        return prompt

    def _get_dimensions(self, aspect_ratio: str) -> tuple:
        """Get dimensions from aspect ratio."""
        dimensions = {
            "1:1": (1024, 1024),
            "16:9": (1024, 576),
            "9:16": (576, 1024),
            "4:3": (1024, 768),
            "3:4": (768, 1024),
        }
        return dimensions.get(aspect_ratio, (1024, 1024))

    def _get_model_version(self, model: str) -> str:
        """Get model version hash for common models."""
        # These would be updated based on Replicate's latest versions
        versions = {
            "black-forest-labs/flux-schnell": "latest",
            "stability-ai/sdxl": "latest",
        }
        return versions.get(model, "latest")

    def get_circuit_status(self) -> Optional[Dict[str, Any]]:
        """Get circuit breaker status."""
        if self.circuit_breaker:
            return self.circuit_breaker.get_status()
        return None

    async def shutdown(self):
        """Clean shutdown."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self._initialized = False
        logger.info("Replicate client shutdown complete")
