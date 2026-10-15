"""Tests for cybersecurity defenses: headers, rate-limiting, secret masking, and payload schemas."""

import pytest
from starlette.testclient import TestClient
from src.dashboard.app import app
from src.utils.security import mask_secret, sanitize_text, RateLimiter

@pytest.fixture
def client():
    return TestClient(app)

def test_security_headers_present(client):
    """Verify all defense-in-depth security headers are attached."""
    res = client.get("/api/health")
    assert res.status_code == 200
    headers = res.headers

    assert "Content-Security-Policy" in headers
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "Strict-Transport-Security" in headers
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "server" not in headers  # Server cloaking

def test_secret_masking():
    """Verify secret masking prevents key leaks."""
    key = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
    masked = mask_secret(key)
    assert masked == "a1b2...c5d6"
    assert key not in masked
    assert mask_secret(None) == ""
    assert mask_secret("") == ""

def test_sanitize_text():
    """Verify regex sanitization redacts hex credentials from strings."""
    raw = "Error communicating with apiKey=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6 failed"
    sanitized = sanitize_text(raw)
    assert "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6" not in sanitized
    assert "a1b2...c5d6" in sanitized

def test_rate_limiter():
    """Verify sliding window rate limiter triggers after threshold."""
    limiter = RateLimiter(max_requests=3, window_seconds=10)
    ip = "192.168.1.100"

    assert limiter.is_allowed(ip)[0] is True
    assert limiter.is_allowed(ip)[0] is True
    assert limiter.is_allowed(ip)[0] is True

    # 4th request must be blocked
    allowed, retry_after = limiter.is_allowed(ip)
    assert allowed is False
    assert retry_after > 0

def test_line_validation_security(client):
    """Verify malicious line update inputs are rejected with 422 Unprocessable Entity."""
    # Negative player_id
    bad1 = client.post("/api/lines", json={"player_id": -5, "stat_type": "PTS", "line": 20.5})
    assert bad1.status_code == 422

    # Malicious stat type injection
    bad2 = client.post("/api/lines", json={"player_id": 1629029, "stat_type": "DROP TABLE", "line": 20.5})
    assert bad2.status_code == 422

    # Unreasonable line
    bad3 = client.post("/api/lines", json={"player_id": 1629029, "stat_type": "PTS", "line": 9999.0})
    assert bad3.status_code == 422

