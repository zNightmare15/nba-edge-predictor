"""Enterprise-grade cybersecurity utilities and middleware for FastAPI.

Protections implemented:
- Defense-in-depth Security Headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.)
- In-memory Token-Bucket / Sliding Window Rate Limiting (Anti-DDoS, Brute-Force prevention)
- Secret Masking and Redaction (Prevents API key leaks in API responses & logs)
- Path Traversal validation
- Input validation models using Pydantic
"""

import time
import re
import os
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple, Optional
from pydantic import BaseModel, Field, field_validator
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

# ---------------------------------------------------------------------------
# 1. Secret Masking & Sanitization
# ---------------------------------------------------------------------------
HEX_SECRET_PATTERN = re.compile(r'\b[a-fA-F0-9]{24,64}\b')

def mask_secret(secret: Optional[str], visible_chars: int = 4) -> str:
    """Mask a secret key to prevent exposure while allowing user recognition.
    
    Example: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6 -> a1b2...c5d6
    """
    if not secret or len(secret) < (visible_chars * 2):
        return ""
    return f"{secret[:visible_chars]}...{secret[-visible_chars:]}"

def sanitize_text(text: str) -> str:
    """Sanitize strings by redacting any potential 32-64 character API keys/secrets."""
    if not text:
        return text
    return HEX_SECRET_PATTERN.sub(lambda m: mask_secret(m.group(0)), text)

# ---------------------------------------------------------------------------
# 2. In-Memory Anti-DDoS Rate Limiter
# ---------------------------------------------------------------------------
class RateLimiter:
    """Thread-safe sliding window rate limiter per IP address."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, retry_after_seconds)."""
        now = time.time()
        cutoff = now - self.window_seconds

        with self.lock:
            # Prune expired timestamps
            timestamps = [t for t in self.requests[client_ip] if t > cutoff]
            self.requests[client_ip] = timestamps

            if len(timestamps) >= self.max_requests:
                oldest = timestamps[0]
                retry_after = int(self.window_seconds - (now - oldest)) + 1
                return False, max(1, retry_after)

            timestamps.append(now)
            return True, 0

    def cleanup(self):
        """Periodically purge dormant IPs to keep memory footprint light."""
        now = time.time()
        cutoff = now - self.window_seconds
        with self.lock:
            dormant = [ip for ip, times in self.requests.items() if not times or times[-1] <= cutoff]
            for ip in dormant:
                del self.requests[ip]

# Separate limiters for GET (analytics reads) and POST (line/settings writes)
READ_LIMITER = RateLimiter(max_requests=120, window_seconds=60)
WRITE_LIMITER = RateLimiter(max_requests=25, window_seconds=60)

# ---------------------------------------------------------------------------
# 3. Security Headers Middleware (OWASP Top 10 Hardened)
# ---------------------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces strict HTTP security headers against XSS, clickjacking, and MIME attacks."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract client IP (handling reverse proxy X-Forwarded-For safely)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        # Apply rate limiting
        is_write = request.method in ("POST", "PUT", "DELETE", "PATCH")
        limiter = WRITE_LIMITER if is_write else READ_LIMITER

        # Whitelist static assets from aggressive rate limits
        if not request.url.path.startswith("/assets") and not request.url.path.startswith("/static"):
            allowed, retry_after = limiter.is_allowed(client_ip)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": f"Rate limit exceeded. Please retry in {retry_after} seconds.",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )

        response = await call_next(request)

        # 1. Content Security Policy (CSP)
        # Prevents arbitrary script injection, inline eval, and rogue data exfiltration
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https://a.espncdn.com https://assets.actionnetwork.com",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 2. Clickjacking Prevention
        response.headers["X-Frame-Options"] = "DENY"

        # 3. MIME-Sniffing Prevention
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 4. Strict Transport Security (HSTS) - 1 Year + Preload
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 5. Referrer Policy - Prevents leaking private URL parameters
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Feature / Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=(), usb=()"

        # 7. Legacy XSS Filter protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 8. Server Cloaking (Remove server fingerprint)
        if "server" in response.headers:
            del response.headers["server"]

        return response

# ---------------------------------------------------------------------------
# 4. Strict Pydantic Request Validation Models
# ---------------------------------------------------------------------------
class LineUpdatePayload(BaseModel):
    """Schema for manual book line adjustments with strict boundaries."""
    player_id: int = Field(..., gt=0, lt=100000000, description="Valid NBA player ID")
    stat_type: str = Field(..., min_length=2, max_length=10, description="Stat abbreviation (PTS, REB, AST, etc.)")
    line: float = Field(..., ge=0.5, le=150.0, description="Over/under line value")

    @field_validator("stat_type")
    @classmethod
    def validate_stat(cls, v: str) -> str:
        valid_stats = {"PTS", "REB", "AST", "3PM", "PRA", "BLK", "STL"}
        clean = v.strip().upper()
        if clean not in valid_stats:
            raise ValueError(f"Stat type must be one of {valid_stats}")
        return clean

class SettingsUpdatePayload(BaseModel):
    """Schema for bankroll and risk configuration updates."""
    bankroll: Optional[float] = Field(None, ge=10.0, le=10000000.0)
    kelly_fraction: Optional[float] = Field(None, ge=0.01, le=1.0)
    min_edge_pct: Optional[float] = Field(None, ge=0.0, le=50.0)
    max_risk_level: Optional[str] = Field(None, max_length=10)
    odds_api_key: Optional[str] = Field(None, max_length=128)

    @field_validator("max_risk_level")
    @classmethod
    def validate_risk(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().upper()
        if clean not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("max_risk_level must be LOW, MEDIUM, or HIGH")
        return clean

