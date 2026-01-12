"""
Blockchain service for Arc network interactions.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict

from eth_account import Account
from web3 import Web3

# web3.py v7+ compatibility
try:
    from web3.middleware import ExtraDataToPOAMiddleware
    poa_middleware = ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware
    poa_middleware = geth_poa_middleware

logger = logging.getLogger(__name__)

ARC_RPC = os.getenv("ARC_RPC_URL", "https://rpc.testnet.arc.network")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
ESCROW_CONTRACT_ADDRESS = os.getenv("ESCROW_CONTRACT_ADDRESS")

DEFAULT_ESCROW_ABI = [
    {
        "type": "function",
        "name": "createEscrow",
        "stateMutability": "payable",
        "inputs": [
            {"name": "seller", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "escrowId", "type": "uint256"}],
    },
    {
        "type": "function",
        "name": "releaseToSeller",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "escrowId", "type": "uint256"}],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "getEscrow",
        "stateMutability": "view",
        "inputs": [{"name": "escrowId", "type": "uint256"}],
        "outputs": [
            {"name": "buyer", "type": "address"},
            {"name": "seller", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "createdAt", "type": "uint256"},
            {"name": "state", "type": "uint8"},
        ],
    },
]


def _load_escrow_abi() -> list[dict[str, Any]]:
    abi_path = Path("contracts/out/SimpleEscrow.sol/SimpleEscrow.json")
    if not abi_path.exists():
        return DEFAULT_ESCROW_ABI
    with abi_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
        return data.get("abi", DEFAULT_ESCROW_ABI)


def _get_web3() -> Web3:
    w3 = Web3(Web3.HTTPProvider(ARC_RPC))
    w3.middleware_onion.inject(poa_middleware, layer=0)
    return w3


def _get_account() -> Account:
    if not AGENT_PRIVATE_KEY:
        raise ValueError("AGENT_PRIVATE_KEY is not set")
    return Account.from_key(AGENT_PRIVATE_KEY)


def _get_contract(w3: Web3):
    if not ESCROW_CONTRACT_ADDRESS:
        raise ValueError("ESCROW_CONTRACT_ADDRESS is not set")
    return w3.eth.contract(
        address=Web3.to_checksum_address(ESCROW_CONTRACT_ADDRESS),
        abi=_load_escrow_abi(),
    )


def _send_with_retry(w3: Web3, transaction: Dict[str, Any], retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            signed = w3.eth.account.sign_transaction(transaction, AGENT_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            logger.info("Broadcasted transaction: %s", tx_hash.hex())
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 1:
                return tx_hash.hex()
            raise RuntimeError("Transaction failed")
        except Exception as exc:
            logger.error("Transaction attempt %s failed: %s", attempt, exc)
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Transaction failed after retries")


def get_agent_balance() -> int:
    w3 = _get_web3()
    account = _get_account()
    balance = w3.eth.get_balance(account.address)
    logger.info("Agent balance fetched for %s", account.address)
    return balance


def estimate_gas(function_name: str, *args: Any) -> int:
    w3 = _get_web3()
    contract = _get_contract(w3)
    function = getattr(contract.functions, function_name)(*args)
    gas = function.estimate_gas()
    logger.info("Estimated gas for %s: %s", function_name, gas)
    return gas


def create_escrow(seller: str, amount: int) -> str:
    w3 = _get_web3()
    account = _get_account()
    contract = _get_contract(w3)
    nonce = w3.eth.get_transaction_count(account.address)
    transaction = contract.functions.createEscrow(seller, amount).build_transaction({
        "from": account.address,
        "value": amount,
        "nonce": nonce,
    })
    logger.info("Creating escrow for seller %s and amount %s", seller, amount)
    return _send_with_retry(w3, transaction)


def release_escrow(escrow_id: int) -> str:
    w3 = _get_web3()
    account = _get_account()
    contract = _get_contract(w3)
    nonce = w3.eth.get_transaction_count(account.address)
    transaction = contract.functions.releaseToSeller(escrow_id).build_transaction({
        "from": account.address,
        "nonce": nonce,
    })
    logger.info("Releasing escrow %s", escrow_id)
    return _send_with_retry(w3, transaction)


def get_escrow_status(escrow_id: int) -> Dict[str, Any]:
    w3 = _get_web3()
    contract = _get_contract(w3)
    escrow = contract.functions.getEscrow(escrow_id).call()
    data = {
        "buyer": escrow[0],
        "seller": escrow[1],
        "amount": escrow[2],
        "created_at": escrow[3],
        "state": escrow[4],
    }
    logger.info("Fetched escrow status for %s", escrow_id)
    return data
