"""Phase 5 claim-control regressions."""

from pathlib import Path

import pytest


@pytest.mark.anyio
async def test_product_search_honors_sort_by_and_limit():
    from agent import CommerceAgent

    agent = CommerceAgent()

    expensive_first = await agent._handle_search_products(
        query="",
        sort_by="price_desc",
        limit=2,
    )

    assert len(expensive_first) == 2
    assert expensive_first[0]["price"] >= expensive_first[1]["price"]
    assert {product["source"] for product in expensive_first} == {"demo_catalog"}

    rating_first = await agent._handle_search_products(
        query="watch sneaker headphones",
        sort_by="rating",
        limit=1,
    )

    assert len(rating_first) == 1
    assert rating_first[0]["name"] == "Minimalist Arc Watch"


@pytest.mark.anyio
async def test_product_search_api_forwards_sort_by_and_limit(monkeypatch):
    import main
    from models.schemas import ProductSearch

    observed = {}

    class FakeAgent:
        async def search_products(self, **kwargs):
            observed.update(kwargs)
            return [
                {
                    "id": "demo_1",
                    "name": "Demo Item",
                    "description": "Demo catalog item",
                    "price": 1.0,
                    "currency": "ARC",
                    "category": "demo",
                    "source": "demo_catalog",
                    "rating": 4.0,
                }
            ]

    monkeypatch.setattr(main, "commerce_agent", FakeAgent())

    result = await main.search_products(
        ProductSearch(query="demo", sort_by="price_asc", limit=1)
    )

    assert observed["sort_by"] == "price_asc"
    assert observed["limit"] == 1
    assert len(result) == 1


@pytest.mark.anyio
async def test_price_comparison_fails_closed_without_live_retailer_integration():
    from tools.price_compare import PriceComparer

    result = await PriceComparer(mode="unavailable").compare("headphones")

    assert result["sources"] == []
    assert result["best_deal"] is None
    assert result["evidence_status"] == "unavailable_no_retailer_integrations"
    assert "not implemented" in result["message"]


@pytest.mark.anyio
async def test_demo_price_comparison_is_labeled_synthetic_and_not_retailer_branded():
    from tools.price_compare import DEMO_PRICE_EVIDENCE, PriceComparer

    result = await PriceComparer(mode="demo").compare("headphones")

    assert result["sources"]
    assert result["evidence_status"] == DEMO_PRICE_EVIDENCE
    assert all(source["evidence_status"] == DEMO_PRICE_EVIDENCE for source in result["sources"])
    assert {"Amazon", "eBay", "Walmart", "BestBuy", "Target"}.isdisjoint(
        {source["source"] for source in result["sources"]}
    )
    assert all(source["url"] is None for source in result["sources"])


def test_public_surfaces_do_not_reintroduce_shipped_nft_or_phantom_api_claims():
    repo_root = Path(__file__).resolve().parents[2]
    surfaces = [
        "README.md",
        "backend/agent.py",
        "frontend/src/app/page.tsx",
        "frontend/src/app/layout.tsx",
        "frontend/src/components/ChatWindow.tsx",
        "frontend/src/components/ProductCard.tsx",
        "HACKATHON-SUBMISSION-PREP.md",
        "SUBMISSION-EXECUTION-PLAN.md",
        "submission/presentation.html",
        "submission/create_pdf.py",
        "video-demo/src/DemoVideo.tsx",
        "video-demo/RECORDING-SCRIPT.md",
        "ui-analysis-context.md",
    ]

    combined = "\n".join((repo_root / path).read_text(encoding="utf-8") for path in surfaces)
    lowered = combined.lower()

    forbidden_claims = [
        "create and manage nft listings",
        "offer to mint it as an nft",
        "mint it as an nft on the arc blockchain",
        "mint as nfts on arc blockchain",
        "mint on arc blockchain to prove creative priority",
        "one-click nft minting",
        "nft ownership proof",
        "agentnft.sol",
        "marketplace.sol",
        "agentwallet.sol",
        "`/api/mint`",
        "`/api/listings`",
        "`/api/purchase`",
        "`/api/agent/status`",
        "nfts minted",
        "total volume",
    ]
    for claim in forbidden_claims:
        assert claim not in lowered

    assert "nft minting is not shipped" in lowered
    assert "simpleescrow" in lowered


def test_legacy_blockchain_service_fails_closed_and_is_not_imported():
    import services.blockchain as legacy

    assert legacy.LEGACY_BLOCKCHAIN_SERVICE_SHIPPED is False
    assert legacy.SHIPPED_ESCROW_SURFACES["verification_module"] == "backend.blockchain"
    assert legacy.SHIPPED_ESCROW_SURFACES["contract"] == "contracts/src/SimpleEscrow.sol"

    with pytest.raises(legacy.LegacyBlockchainServiceUnavailable, match="retired"):
        legacy.create_escrow("0x0000000000000000000000000000000000000001", 1)

    with pytest.raises(legacy.LegacyBlockchainServiceUnavailable, match="retired"):
        legacy.release_escrow(1)

    backend_root = Path(__file__).resolve().parents[1]
    retired_module = backend_root / "services" / "blockchain.py"
    production_files = [
        path
        for path in backend_root.rglob("*.py")
        if "tests" not in path.parts and path.resolve() != retired_module.resolve()
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in production_files)

    forbidden_imports = [
        "import services.blockchain",
        "from services.blockchain",
        "from services import blockchain",
        "backend.services.blockchain",
    ]
    for import_text in forbidden_imports:
        assert import_text not in combined
