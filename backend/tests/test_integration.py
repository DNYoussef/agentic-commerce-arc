"""
Integration tests for chat and product endpoints.
"""

from uuid import uuid4
import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def stub_commerce_agent(monkeypatch):
    import main

    class DummyAgent:
        async def process_message(self, message: str, user_id: str, context: dict):
            return {
                "message": "ok",
                "actions": [],
                "products": [],
                "images": [],
            }

        async def search_products(self, query: str, category=None, max_price=None, min_price=None):
            return [
                {
                    "id": "prod_test",
                    "name": "Test Product",
                    "description": "Test description",
                    "price": 9.99,
                    "currency": "USD",
                    "category": "test",
                    "image_url": None,
                    "source": "test",
                    "rating": 4.5,
                    "reviews_count": 10,
                    "in_stock": True,
                    "url": None,
                }
            ]

        async def compare_prices(self, product_id: str):
            return {
                "product_name": "Test Product",
                "product_id": product_id,
                "sources": [
                    {
                        "source": "test",
                        "price": 9.99,
                        "currency": "USD",
                        "url": None,
                        "in_stock": True,
                        "shipping": None,
                        "total": 9.99,
                    }
                ],
                "best_deal": {
                    "source": "test",
                    "price": 9.99,
                    "shipping": None,
                    "total": 9.99,
                    "currency": "USD",
                    "url": None,
                    "in_stock": True,
                    "savings": 0,
                    "savings_percent": 0,
                },
                "fetched_at": datetime.utcnow().isoformat(),
                "cached": False,
            }

        async def generate_product_image(self, prompt: str, style: str, aspect_ratio: str):
            return {
                "image_url": "https://example.com/test.png",
                "prompt": prompt,
                "style": style,
                "model": "test",
                "prediction_id": None,
                "error": None,
            }

    monkeypatch.setattr(main, "commerce_agent", DummyAgent())


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _register_user(async_client: AsyncClient) -> str:
    payload = {
        "email": f"user_{uuid4().hex}@example.com",
        "password": "TestPassword123!",
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.mark.anyio
async def test_chat_endpoint_returns_response(async_client: AsyncClient):
    token = await _register_user(async_client)
    response = await async_client.post(
        "/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Show me a cool jacket", "context": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.anyio
async def test_product_search(async_client: AsyncClient):
    token = await _register_user(async_client)
    response = await async_client.post(
        "/products/search",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "sneaker"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data


@pytest.mark.anyio
async def test_image_generation_mock(async_client: AsyncClient):
    token = await _register_user(async_client)
    response = await async_client.post(
        "/images/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": "Minimalist watch", "style": "minimalist", "aspect_ratio": "1:1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data


@pytest.mark.anyio
async def test_price_comparison(async_client: AsyncClient):
    token = await _register_user(async_client)
    response = await async_client.post(
        "/products/compare",
        headers={"Authorization": f"Bearer {token}"},
        json={"product_id": "prod_001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data


def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/chat/test-user") as websocket:
        websocket.send_json({"type": "ping"})
        message = websocket.receive_json()
        assert message["type"] in {"pong", "ping"}


@pytest.mark.skipif(os.getenv("TESTING") == "true", reason="requires live agent streaming")
def test_websocket_streaming():
    client = TestClient(app)
    with client.websocket_connect("/ws/chat/test-user") as websocket:
        websocket.send_json({"type": "message", "content": "Hello there"})
        received_done = False
        for _ in range(20):
            message = websocket.receive_json()
            if message["type"] == "done":
                received_done = True
                break
        assert received_done
