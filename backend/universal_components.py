"""Universal component wiring for agentic-commerce-arc backend.

Gracefully handles missing library dependencies for CI/testing environments.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional, Protocol

logger = logging.getLogger(__name__)

# Try to load Claude library components (optional)
LIBRARY_ROOT = Path(os.getenv("CLAUDE_LIBRARY_ROOT", r"C:\Users\17175\.claude"))
_library_available = False

if LIBRARY_ROOT.exists():
    sys.path.insert(0, str(LIBRARY_ROOT))
    try:
        from library.components.cognitive_architecture.integration.connascence_bridge import ConnascenceBridge
        from library.components.cognitive_architecture.integration.telemetry_bridge import TelemetryBridge
        from library.components.memory.memory_mcp_client import create_memory_mcp_client
        from library.components.observability.tagging_protocol import TaggingProtocol, create_simple_tagger
        _library_available = True
    except ImportError:
        logger.warning("Claude library components not available - using stubs")


# Stub implementations for when library is unavailable
class TaggingProtocol(Protocol):
    """Protocol for tagging operations."""
    def tag(self, key: str, value: Any) -> None: ...


class StubTagger:
    """Stub tagger for environments without library."""
    def __init__(self, agent_id: str, project_id: str):
        self.agent_id = agent_id
        self.project_id = project_id

    def tag(self, key: str, value: Any) -> None:
        pass


class StubMemoryClient:
    """Stub memory client for environments without library."""
    async def store(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def retrieve(self, *args: Any, **kwargs: Any) -> list:
        return []


class StubTelemetryBridge:
    """Stub telemetry bridge for environments without library."""
    def __init__(self, loop_dir: Path):
        self.loop_dir = loop_dir

    def emit(self, *args: Any, **kwargs: Any) -> None:
        pass


class StubConnascenceBridge:
    """Stub connascence bridge for environments without library."""
    def analyze(self, *args: Any, **kwargs: Any) -> dict:
        return {}


def init_tagger() -> Any:
    if _library_available:
        return create_simple_tagger(agent_id="agentic-commerce-arc", project_id="agentic-commerce-arc")
    return StubTagger(agent_id="agentic-commerce-arc", project_id="agentic-commerce-arc")


def init_memory_client() -> Any:
    if _library_available:
        endpoint = os.getenv("MEMORY_MCP_URL", "http://localhost:3000")
        return create_memory_mcp_client(
            project_id="agentic-commerce-arc",
            project_name="agentic-commerce-arc",
            agent_id="agentic-commerce-arc",
            agent_category="backend",
            capabilities=["commerce", "payments", "orchestration"],
            mcp_endpoint=endpoint,
        )
    return StubMemoryClient()


def init_telemetry_bridge(loop_dir: Optional[str] = None) -> Any:
    resolved = Path(loop_dir) if loop_dir else Path(".loop")
    if _library_available:
        return TelemetryBridge(loop_dir=resolved)
    return StubTelemetryBridge(loop_dir=resolved)


def init_connascence_bridge() -> Any:
    if _library_available:
        return ConnascenceBridge()
    return StubConnascenceBridge()

