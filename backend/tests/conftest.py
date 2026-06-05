"""
Pytest configuration and fixtures for backend tests.
"""

import os
import secrets
import pytest

# Set testing environment
os.environ["TESTING"] = "true"
os.environ.setdefault("JWT_SECRET_KEY", secrets.token_urlsafe(48))
# Use DATABASE_PATH to match database.py (not DATABASE_URL which is ignored)
os.environ["DATABASE_PATH"] = "./test_data/test.db"


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for all async tests."""
    return "asyncio"
