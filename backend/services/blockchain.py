"""Retired blockchain service compatibility surface.

The shipped escrow verification code lives in ``backend/blockchain.py`` and the
on-chain escrow implementation lives in ``contracts/src/SimpleEscrow.sol``. This
legacy service module is intentionally kept as a fail-closed surface so stale
imports cannot present dead transaction helpers as shipped functionality.
"""

from __future__ import annotations

from typing import Any


LEGACY_BLOCKCHAIN_SERVICE_SHIPPED = False
SHIPPED_ESCROW_SURFACES = {
    "verification_module": "backend.blockchain",
    "contract": "contracts/src/SimpleEscrow.sol",
}


class LegacyBlockchainServiceUnavailable(RuntimeError):
    """Raised when stale code tries to use the retired service module."""


def _raise_retired(function_name: str) -> None:
    raise LegacyBlockchainServiceUnavailable(
        f"backend.services.blockchain.{function_name} is retired; "
        "use backend.blockchain for shipped escrow verification."
    )


def get_agent_balance() -> int:
    _raise_retired("get_agent_balance")


def estimate_gas(function_name: str, *args: Any) -> int:
    _raise_retired("estimate_gas")


def create_escrow(seller: str, amount: int) -> str:
    _raise_retired("create_escrow")


def release_escrow(escrow_id: int) -> str:
    _raise_retired("release_escrow")


def get_escrow_status(escrow_id: int) -> dict[str, Any]:
    _raise_retired("get_escrow_status")


__all__ = [
    "LEGACY_BLOCKCHAIN_SERVICE_SHIPPED",
    "SHIPPED_ESCROW_SURFACES",
    "LegacyBlockchainServiceUnavailable",
    "create_escrow",
    "estimate_gas",
    "get_agent_balance",
    "get_escrow_status",
    "release_escrow",
]
