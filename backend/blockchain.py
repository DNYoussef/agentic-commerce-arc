"""
Blockchain utilities for Arc transactions.

Provides helpers for verifying escrow transactions on-chain.
"""

import json
import os
from typing import Any, Dict, Optional

from web3 import Web3

# web3.py v7+ compatibility
try:
    from web3.middleware import ExtraDataToPOAMiddleware
    poa_middleware = ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware
    poa_middleware = geth_poa_middleware

ARC_RPC_URL = os.getenv("ALCHEMY_ARC_RPC") or os.getenv("ARC_RPC_URL") or "http://127.0.0.1:8545"

ESCROW_ABI = [
    {
        "type": "event",
        "name": "EscrowCreated",
        "inputs": [
            {"name": "escrowId", "type": "uint256", "indexed": True},
            {"name": "buyer", "type": "address", "indexed": True},
            {"name": "seller", "type": "address", "indexed": True},
            {"name": "amount", "type": "uint256", "indexed": False},
        ],
        "anonymous": False,
    },
]


def get_web3() -> Web3:
    """Return a configured Web3 instance."""
    w3 = Web3(Web3.HTTPProvider(ARC_RPC_URL))
    w3.middleware_onion.inject(poa_middleware, layer=0)
    return w3


def verify_escrow_transaction(
    tx_hash: str,
    escrow_address: str,
    expected_buyer: Optional[str] = None,
    expected_seller: Optional[str] = None,
    expected_amount: Optional[int] = None,
) -> Dict[str, Any]:
    """Verify an escrow transaction receipt and emitted event."""
    w3 = get_web3()
    receipt = w3.eth.get_transaction_receipt(tx_hash)

    if receipt is None:
        return {"status": "pending", "verified": False}

    if receipt.status != 1:
        return {"status": "failed", "verified": False}

    escrow_address = Web3.to_checksum_address(escrow_address)
    if receipt.to and Web3.to_checksum_address(receipt.to) != escrow_address:
        return {"status": "failed", "verified": False, "reason": "tx_to_mismatch"}

    contract = w3.eth.contract(address=escrow_address, abi=ESCROW_ABI)
    events = contract.events.EscrowCreated().process_receipt(receipt)
    if not events:
        return {"status": "failed", "verified": False, "reason": "missing_event"}

    event = events[0]
    buyer = Web3.to_checksum_address(event["args"]["buyer"])
    seller = Web3.to_checksum_address(event["args"]["seller"])
    amount = int(event["args"]["amount"])

    if expected_buyer and Web3.to_checksum_address(expected_buyer) != buyer:
        return {"status": "failed", "verified": False, "reason": "buyer_mismatch"}

    if expected_seller and Web3.to_checksum_address(expected_seller) != seller:
        return {"status": "failed", "verified": False, "reason": "seller_mismatch"}

    if expected_amount is not None and expected_amount != amount:
        return {"status": "failed", "verified": False, "reason": "amount_mismatch"}

    return {
        "status": "confirmed",
        "verified": True,
        "escrow_id": str(event["args"]["escrowId"]),
        "buyer": buyer,
        "seller": seller,
        "amount": amount,
        "raw_event": json.loads(Web3.to_json(event["args"])),
    }
