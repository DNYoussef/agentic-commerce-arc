"""Phase 4 security regressions."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_testing_mode_does_not_enable_hardcoded_jwt_secret():
    backend_root = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": str(backend_root),
        "TESTING": "true",
    }
    env.pop("JWT_SECRET_KEY", None)

    result = subprocess.run(
        [sys.executable, "-c", "import auth"],
        cwd=backend_root,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "JWT_SECRET_KEY environment variable is required" in result.stderr


def test_blockchain_rejects_malformed_tx_hash_before_rpc(monkeypatch):
    import blockchain

    def fail_get_web3():
        raise AssertionError("malformed tx hash must not reach the RPC client")

    monkeypatch.setattr(blockchain, "get_web3", fail_get_web3)

    result = blockchain.verify_escrow_transaction(
        tx_hash="not-a-transaction-hash",
        escrow_address="0x" + "1" * 40,
    )

    assert result == {
        "status": "failed",
        "verified": False,
        "reason": "invalid_tx_hash",
    }


@pytest.mark.anyio
async def test_transaction_verify_rejects_malformed_tx_hash_before_db_or_rpc(monkeypatch):
    import main
    from models.schemas import TransactionVerifyRequest

    async def fail_db_lookup(*_args, **_kwargs):
        raise AssertionError("malformed tx hash must not reach transaction storage")

    def fail_chain_verify(*_args, **_kwargs):
        raise AssertionError("malformed tx hash must not reach chain verification")

    monkeypatch.setattr(main, "get_transaction_by_hash", fail_db_lookup)
    monkeypatch.setattr(main, "get_transaction_by_idempotency_key", fail_db_lookup)
    monkeypatch.setattr(main, "verify_escrow_transaction", fail_chain_verify)

    payload = TransactionVerifyRequest(
        tx_hash="../not-a-tx",
        escrow_address="0x" + "1" * 40,
    )

    with pytest.raises(main.HTTPException) as excinfo:
        await main.verify_transaction(payload, {"sub": "1"})

    assert excinfo.value.status_code == 400
    assert "32-byte 0x-prefixed hex" in excinfo.value.detail
