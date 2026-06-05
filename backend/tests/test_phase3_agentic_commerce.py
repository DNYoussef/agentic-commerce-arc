import asyncio
from datetime import datetime

import pytest
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect

import main
from tools.price_compare import PriceComparer, PriceResult, stable_hash_int
from tools.replicate import ReplicateClient


def test_transaction_verify_rejects_non_numeric_subject_without_value_error():
    with pytest.raises(HTTPException) as excinfo:
        main._current_user_id({"sub": "wallet-user"})

    assert excinfo.value.status_code == 401
    assert "numeric database id" in excinfo.value.detail


@pytest.mark.anyio
async def test_replicate_success_without_output_url_fails_closed():
    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeClient:
        async def post(self, *args, **kwargs):
            return FakeResponse({"id": "prediction-1"})

        async def get(self, *args, **kwargs):
            return FakeResponse({"status": "succeeded", "output": []})

    client = ReplicateClient()
    client.client = FakeClient()

    with pytest.raises(Exception, match="without an output image URL"):
        await client._create_prediction("owner/model", "prompt", 512, 512)


def test_price_hash_is_stable_and_base_price_repeats():
    comparer = PriceComparer()

    assert stable_hash_int("premium headphones") == stable_hash_int("premium headphones")
    assert comparer._generate_base_price("premium headphones") == comparer._generate_base_price("premium headphones")


def test_best_deal_savings_uses_in_stock_comparison_pool():
    comparer = PriceComparer()
    fetched_at = datetime.utcnow()
    results = [
        PriceResult("Outlier", 1000.0, "USD", None, False, 0.0, fetched_at),
        PriceResult("A", 100.0, "USD", None, True, 0.0, fetched_at),
        PriceResult("B", 200.0, "USD", None, True, 0.0, fetched_at),
    ]

    best = comparer._find_best_deal(results, include_shipping=True)

    assert best is not None
    assert best["source"] == "A"
    assert best["savings"] == 50.0
    assert best["savings_percent"] == 33.3


@pytest.mark.anyio
async def test_websocket_disconnect_cancels_inflight_agent_stream(monkeypatch):
    stream_started = asyncio.Event()
    stream_cancelled = asyncio.Event()

    class FakeWebSocket:
        headers = {}
        query_params = {}

        def __init__(self):
            self.receive_count = 0
            self.sent = []

        async def accept(self, subprotocol=None):
            self.subprotocol = subprotocol

        async def close(self, code=1000, reason=None):
            self.closed = (code, reason)

        async def receive_json(self):
            self.receive_count += 1
            if self.receive_count == 1:
                return {"type": "message", "content": "find a jacket", "context": {}}
            await stream_started.wait()
            raise WebSocketDisconnect(code=1000)

        async def send_json(self, message):
            self.sent.append(message)

    async def fake_authenticate(websocket, path_user_id):
        return path_user_id, None

    async def fake_stream(websocket, user_id, content, context):
        stream_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            stream_cancelled.set()

    monkeypatch.setattr(main, "_authenticate_websocket", fake_authenticate)
    monkeypatch.setattr(main, "_stream_agent_response", fake_stream)

    await main.websocket_chat(FakeWebSocket(), "user-1")

    assert stream_cancelled.is_set()
