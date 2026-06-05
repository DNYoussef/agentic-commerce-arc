"""
Price Comparison Tool.

Live retailer price integrations are not implemented in this repository. The
default behavior is fail-closed with an explicit unavailable status. A local demo
mode can be enabled for UI testing, and every demo result is labeled synthetic.

Features:
- Explicit unavailable status when no live source is configured
- Optional synthetic demo aggregation
- Result caching with TTL
- Best deal identification
- Price history tracking

COM-006: Removed false rate limiting claim; only caching is implemented.
"""

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from database import get_db_context, DatabaseSession

logger = logging.getLogger(__name__)

# Configuration
CACHE_TTL_MINUTES = int(os.getenv("PRICE_CACHE_TTL_MINUTES", "60"))
PRICE_COMPARE_MODE = os.getenv("PRICE_COMPARE_MODE", "unavailable").strip().lower()
DEMO_PRICE_EVIDENCE = "synthetic_demo_not_retailer_quote"
UNAVAILABLE_EVIDENCE = "unavailable_no_retailer_integrations"


def stable_hash_int(value: str) -> int:
    """Return a deterministic integer hash for mock pricing calculations."""
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


@dataclass
class PriceSource:
    """Configuration for a price source."""
    name: str
    base_url: str
    api_key: Optional[str] = None
    enabled: bool = True


@dataclass
class PriceResult:
    """Result from a price source."""
    source: str
    price: float
    currency: str
    url: Optional[str]
    in_stock: bool
    shipping: Optional[float]
    fetched_at: datetime


class PriceComparer:
    """
    Compare prices when live sources are configured.

    This build has no live retailer API integrations. By default it returns an
    unavailable response rather than fabricated prices. Set
    PRICE_COMPARE_MODE=demo to return labeled synthetic data for UI exercises.
    """

    # Demo-only sources. These names intentionally avoid real retailer branding.
    SOURCES = [
        PriceSource("DemoMart", "demo://mart"),
        PriceSource("SampleOutlet", "demo://outlet"),
        PriceSource("PrototypeShop", "demo://shop"),
        PriceSource("SandboxSupply", "demo://supply"),
        PriceSource("ExampleRetail", "demo://retail"),
    ]

    def __init__(self, mode: Optional[str] = None):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=CACHE_TTL_MINUTES)
        self.client: Optional[httpx.AsyncClient] = None
        self.mode = (mode or PRICE_COMPARE_MODE or "unavailable").strip().lower()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client

    async def compare(
        self,
        product_name: str,
        product_id: Optional[str] = None,
        include_shipping: bool = True
    ) -> Dict[str, Any]:
        """
        Compare prices for a product across all sources.

        Args:
            product_name: Name of the product to search
            product_id: Optional product identifier
            include_shipping: Include shipping costs in comparison

        Returns:
            Dict with sources, prices, and best deal information
        """
        if self.mode not in {"demo", "synthetic_demo"}:
            return self._unavailable_response(product_name, product_id)

        cache_key = f"{product_name}:{product_id or 'none'}"

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            logger.debug(f"Cache hit for {cache_key}")
            return cached

        # Fetch prices from all sources
        results = await self._fetch_all_prices(product_name, product_id)

        # Calculate best deal
        best_deal = self._find_best_deal(results, include_shipping)

        # Build response
        response = {
            "product_name": product_name,
            "product_id": product_id,
            "sources": [
                {
                    "source": r.source,
                    "price": r.price,
                    "currency": r.currency,
                    "url": r.url,
                    "in_stock": r.in_stock,
                    "shipping": r.shipping,
                    "total": r.price + (r.shipping or 0) if include_shipping else r.price,
                    "evidence_status": DEMO_PRICE_EVIDENCE,
                }
                for r in results
            ],
            "best_deal": best_deal,
            "fetched_at": datetime.utcnow().isoformat(),
            "cached": False,
            "evidence_status": DEMO_PRICE_EVIDENCE,
            "message": "Synthetic demo prices only; no retailer quote was fetched.",
        }

        # Cache results
        self._set_cached(cache_key, response)

        # Do not persist synthetic demo prices as price history.

        return response

    def _unavailable_response(self, product_name: str, product_id: Optional[str]) -> Dict[str, Any]:
        return {
            "product_name": product_name,
            "product_id": product_id,
            "sources": [],
            "best_deal": None,
            "fetched_at": datetime.utcnow().isoformat(),
            "cached": False,
            "evidence_status": UNAVAILABLE_EVIDENCE,
            "message": "Live retailer price comparison is not implemented in this build.",
        }

    async def _fetch_all_prices(
        self,
        product_name: str,
        product_id: Optional[str]
    ) -> List[PriceResult]:
        """Fetch prices from all enabled sources concurrently."""
        tasks = []
        for source in self.SOURCES:
            if source.enabled:
                tasks.append(self._fetch_price_from_source(source, product_name, product_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors and None results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Error fetching from {self.SOURCES[i].name}: {result}")
            elif result is not None:
                valid_results.append(result)

        return valid_results

    async def _fetch_price_from_source(
        self,
        source: PriceSource,
        product_name: str,
        product_id: Optional[str]
    ) -> Optional[PriceResult]:
        """
        Fetch price from a single source.

        Demo mode returns synthetic values for UI exercises only. These are not
        retailer quotes and must remain labeled as synthetic in API responses.
        """
        # Simulate API call delay
        await asyncio.sleep(0.1 + (stable_hash_int(source.name) % 10) / 100)

        # Generate realistic mock prices based on product and source
        base_price = self._generate_base_price(product_name)
        price_variation = self._get_source_price_variation(source.name)
        shipping_cost = self._get_shipping_cost(source.name)

        price = round(base_price * price_variation, 2)

        return PriceResult(
            source=source.name,
            price=price,
            currency="USD",
            url=None,
            in_stock=stable_hash_int(f"{product_name}:{source.name}") % 10 > 2,  # 80% in stock
            shipping=shipping_cost,
            fetched_at=datetime.utcnow()
        )

    def _generate_base_price(self, product_name: str) -> float:
        """Generate a base price based on product name."""
        # Use product name hash for consistent pricing
        name_hash = stable_hash_int(product_name.lower())

        # Categorize by price range based on keywords
        expensive_keywords = ["luxury", "premium", "pro", "max", "ultra"]
        cheap_keywords = ["budget", "basic", "mini", "lite"]

        name_lower = product_name.lower()

        if any(kw in name_lower for kw in expensive_keywords):
            base = 200 + (name_hash % 500)
        elif any(kw in name_lower for kw in cheap_keywords):
            base = 20 + (name_hash % 80)
        else:
            base = 50 + (name_hash % 200)

        return float(base)

    def _get_source_price_variation(self, source_name: str) -> float:
        """Get price variation multiplier for a source."""
        variations = {
            "DemoMart": 1.0,
            "SampleOutlet": 0.92,
            "PrototypeShop": 0.95,
            "SandboxSupply": 1.05,
            "ExampleRetail": 1.02,
        }
        return variations.get(source_name, 1.0)

    def _get_shipping_cost(self, source_name: str) -> Optional[float]:
        """Get typical shipping cost for a source."""
        shipping = {
            "DemoMart": 0.0,
            "SampleOutlet": 5.99,
            "PrototypeShop": 0.0,
            "SandboxSupply": 0.0,
            "ExampleRetail": 5.99,
        }
        return shipping.get(source_name, 7.99)

    def _find_best_deal(
        self,
        results: List[PriceResult],
        include_shipping: bool
    ) -> Optional[Dict[str, Any]]:
        """Find the best deal among results."""
        if not results:
            return None

        # Calculate total price for each result
        def total_price(r: PriceResult) -> float:
            if include_shipping and r.shipping:
                return r.price + r.shipping
            return r.price

        # Filter to in-stock items
        in_stock_results = [r for r in results if r.in_stock]
        comparison_pool = in_stock_results or results  # Fall back to all if none in stock

        # Find minimum
        best = min(comparison_pool, key=total_price)

        # Calculate savings against comparable in-stock options only.
        avg_price = sum(total_price(r) for r in comparison_pool) / len(comparison_pool)
        savings = avg_price - total_price(best)

        return {
            "source": best.source,
            "price": best.price,
            "shipping": best.shipping,
            "total": total_price(best),
            "currency": best.currency,
            "url": best.url,
            "in_stock": best.in_stock,
            "savings": round(savings, 2),
            "savings_percent": round((savings / avg_price) * 100, 1) if avg_price > 0 else 0,
            "evidence_status": DEMO_PRICE_EVIDENCE,
        }

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if still valid."""
        if key not in self.cache:
            return None

        cached = self.cache[key]
        cached_at = datetime.fromisoformat(cached.get("fetched_at", "1970-01-01"))

        if datetime.utcnow() - cached_at > self.cache_ttl:
            del self.cache[key]
            return None

        # Mark as cached
        cached["cached"] = True
        return cached

    def _set_cached(self, key: str, data: Dict[str, Any]):
        """Cache a result."""
        self.cache[key] = data

        # Simple cache size limit
        if len(self.cache) > 1000:
            # Remove oldest entries
            keys_to_remove = list(self.cache.keys())[:100]
            for k in keys_to_remove:
                del self.cache[k]

    async def _save_to_database(
        self,
        product_name: str,
        product_id: Optional[str],
        results: List[PriceResult]
    ):
        """Save price comparison results to database."""
        try:
            expires_at = datetime.utcnow() + self.cache_ttl

            async with DatabaseSession() as session:
                for result in results:
                    await session.execute(
                        """
                        INSERT INTO price_comparisons
                        (product_id, source, price, currency, url, fetched_at, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            product_id or product_name,
                            result.source,
                            result.price,
                            result.currency,
                            result.url,
                            result.fetched_at.isoformat(),
                            expires_at.isoformat()
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to save price comparison: {e}")

    async def get_price_history(
        self,
        product_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price history for a product."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        async with get_db_context() as db:
            cursor = await db.execute(
                """
                SELECT source, price, currency, fetched_at
                FROM price_comparisons
                WHERE product_id = ? AND fetched_at > ?
                ORDER BY fetched_at DESC
                """,
                (product_id, cutoff)
            )
            rows = await cursor.fetchall()

            return [
                {
                    "source": row[0],
                    "price": row[1],
                    "currency": row[2],
                    "fetched_at": row[3]
                }
                for row in rows
            ]

    def clear_cache(self):
        """Clear the price cache."""
        self.cache.clear()
        logger.info("Price cache cleared")

    async def shutdown(self):
        """Clean shutdown."""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.cache.clear()
