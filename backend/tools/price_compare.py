"""
Price Comparison Tool - Compare prices across multiple sources.

Provides product price comparison across various e-commerce platforms
with caching and rate limiting.

Features:
- Multi-source price aggregation
- Result caching with TTL
- Best deal identification
- Price history tracking
"""

import asyncio
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
    Compare prices across multiple e-commerce sources.

    Aggregates prices from various sources and identifies the best deals.
    Uses caching to reduce API calls and improve performance.
    """

    # Configured price sources (would be replaced with actual integrations)
    SOURCES = [
        PriceSource("Amazon", "https://api.amazon.com"),
        PriceSource("eBay", "https://api.ebay.com"),
        PriceSource("Walmart", "https://api.walmart.com"),
        PriceSource("BestBuy", "https://api.bestbuy.com"),
        PriceSource("Target", "https://api.target.com"),
    ]

    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=CACHE_TTL_MINUTES)
        self.client: Optional[httpx.AsyncClient] = None

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
                }
                for r in results
            ],
            "best_deal": best_deal,
            "fetched_at": datetime.utcnow().isoformat(),
            "cached": False
        }

        # Cache results
        self._set_cached(cache_key, response)

        # Save to database for history
        await self._save_to_database(product_name, product_id, results)

        return response

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

        Note: In production, this would integrate with actual retailer APIs.
        For hackathon, we return mock data with realistic variations.
        """
        # Simulate API call delay
        await asyncio.sleep(0.1 + (hash(source.name) % 10) / 100)

        # Generate realistic mock prices based on product and source
        base_price = self._generate_base_price(product_name)
        price_variation = self._get_source_price_variation(source.name)
        shipping_cost = self._get_shipping_cost(source.name)

        price = round(base_price * price_variation, 2)

        return PriceResult(
            source=source.name,
            price=price,
            currency="USD",
            url=f"https://{source.name.lower()}.com/search?q={product_name.replace(' ', '+')}",
            in_stock=hash(f"{product_name}{source.name}") % 10 > 2,  # 80% in stock
            shipping=shipping_cost,
            fetched_at=datetime.utcnow()
        )

    def _generate_base_price(self, product_name: str) -> float:
        """Generate a base price based on product name."""
        # Use product name hash for consistent pricing
        name_hash = abs(hash(product_name.lower()))

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
            "Amazon": 1.0,      # Reference price
            "eBay": 0.92,       # Often cheaper
            "Walmart": 0.95,    # Slightly cheaper
            "BestBuy": 1.05,    # Slightly more expensive
            "Target": 1.02,     # About average
        }
        return variations.get(source_name, 1.0)

    def _get_shipping_cost(self, source_name: str) -> Optional[float]:
        """Get typical shipping cost for a source."""
        shipping = {
            "Amazon": 0.0,      # Free with Prime
            "eBay": 5.99,       # Variable
            "Walmart": 0.0,     # Free pickup
            "BestBuy": 0.0,     # Free pickup
            "Target": 5.99,     # Standard shipping
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
        if not in_stock_results:
            in_stock_results = results  # Fall back to all if none in stock

        # Find minimum
        best = min(in_stock_results, key=total_price)

        # Calculate savings vs average
        avg_price = sum(total_price(r) for r in results) / len(results)
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
            "savings_percent": round((savings / avg_price) * 100, 1) if avg_price > 0 else 0
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
