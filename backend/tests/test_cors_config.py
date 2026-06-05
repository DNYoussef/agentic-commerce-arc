from main import _build_cors_origins


def test_cors_config_ignores_wildcards(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*,https://frontend.example.com")
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    monkeypatch.delenv("NEXT_PUBLIC_APP_URL", raising=False)
    monkeypatch.delenv("FRONTEND_PUBLIC_DOMAIN", raising=False)
    monkeypatch.delenv("RAILWAY_PUBLIC_DOMAIN", raising=False)

    origins = _build_cors_origins()

    assert origins == ["https://frontend.example.com"]


def test_cors_config_includes_railway_domains(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("FRONTEND_PUBLIC_DOMAIN", "frontend-production-dd6f.up.railway.app")
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "agentic-commerce-arc-production.up.railway.app")

    origins = _build_cors_origins()

    assert "https://frontend-production-dd6f.up.railway.app" in origins
    assert "https://agentic-commerce-arc-production.up.railway.app" in origins
