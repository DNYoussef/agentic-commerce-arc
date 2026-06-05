"""
Blockchain utilities for Arc transactions.

Provides helpers for verifying escrow transactions on-chain.

COM-005: Added graceful error handling for RPC failures.
"""

import json
import logging
import os
import re
from typing import Any, Dict, Optional

from web3 import Web3
from web3.exceptions import TransactionNotFound, ContractLogicError

# web3.py v7+ compatibility
try:
    from web3.middleware import ExtraDataToPOAMiddleware
    poa_middleware = ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware
    poa_middleware = geth_poa_middleware

logger = logging.getLogger(__name__)

ARC_RPC_URL = os.getenv("ALCHEMY_ARC_RPC") or os.getenv("ARC_RPC_URL") or "http://127.0.0.1:8545"
_TX_HASH_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")


class InvalidTransactionHash(ValueError):
    """Raised when a transaction hash is not a 32-byte hex value."""


def normalize_tx_hash(tx_hash: str) -> str:
    """Return a normalized 0x-prefixed transaction hash or raise."""
    if not isinstance(tx_hash, str) or not _TX_HASH_RE.fullmatch(tx_hash):
        raise InvalidTransactionHash("Transaction hash must be a 32-byte 0x-prefixed hex value.")
    return tx_hash.lower()

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
    """
    Verify an escrow transaction receipt and emitted event.

    COM-005: Handles RPC failures gracefully instead of raising exceptions.
    Returns pending/failed status with reason on error.
    """
    try:
        tx_hash = normalize_tx_hash(tx_hash)
    except InvalidTransactionHash:
        return {"status": "failed", "verified": False, "reason": "invalid_tx_hash"}

    try:
        w3 = get_web3()
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except TransactionNotFound:
        # COM-005: Transaction not yet mined or invalid hash
        logger.debug(f"Transaction not found: {tx_hash}")
        return {"status": "pending", "verified": False, "reason": "tx_not_found"}
    except ConnectionError as e:
        # COM-005: RPC connection failed
        logger.warning(f"RPC connection error for {tx_hash}: {e}")
        return {"status": "pending", "verified": False, "reason": "rpc_connection_error"}
    except Exception as e:
        # COM-005: Catch other web3 exceptions (invalid hash format, etc.)
        logger.warning(f"Error fetching transaction {tx_hash}: {e}")
        return {"status": "pending", "verified": False, "reason": f"rpc_error: {type(e).__name__}"}

    if receipt is None:
        return {"status": "pending", "verified": False}

    if receipt.status != 1:
        return {"status": "failed", "verified": False}

    try:
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
    except ContractLogicError as e:
        # COM-005: Contract execution error
        logger.warning(f"Contract error for {tx_hash}: {e}")
        return {"status": "failed", "verified": False, "reason": f"contract_error: {str(e)}"}
    except Exception as e:
        # COM-005: Catch unexpected errors during event processing
        logger.error(f"Unexpected error verifying {tx_hash}: {e}")
        return {"status": "failed", "verified": False, "reason": f"verification_error: {type(e).__name__}"}
