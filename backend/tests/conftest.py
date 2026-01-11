"""
Pytest configuration and fixtures for backend tests.
"""

import os
import pytest

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for all async tests."""
    return "asyncio"
