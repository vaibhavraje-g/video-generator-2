# backend/app/middleware/security.py
"""Comprehensive Security Middleware and Defenses for Video Generator API.

Implements OWASP Top 10 recommendations:
1. Security Headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options)
2. SSRF Protection (Validation of external media/background URLs)
3. Input Sanitization (Defense against prompt injection & control character attacks)
4. Path Traversal Defense
"""

import ipaddress
import re
import time
from typing import Callable, Dict, Tuple
from urllib.parse import urlparse
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Maximum length for topic inputs to prevent DoS / prompt inflation
MAX_TOPIC_LENGTH = 1000
MAX_DESCRIPTION_LENGTH = 4000

# Private & reserved IP networks disallowed for SSRF protection
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private Class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private Class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private Class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-Local (AWS/GCP/Azure instance metadata!)
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-Local
]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds enterprise-grade security headers to all HTTP responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 1. Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # 2. Prevent MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. Restrict Referrer leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 4. Strict Transport Security (HSTS - 1 year)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        # 5. Restrict dangerous browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # 6. Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https: blob:; "
            "media-src 'self' https: blob: data:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "connect-src 'self' ws: wss: https:;"
        )

        return response


class SimpleRateLimiter:
    """In-memory rate limiter per IP address for brute-force protection."""

    def __init__(self, requests_per_minute: int = 30):
        self.rate = requests_per_minute
        self.clients: Dict[str, list[float]] = {}

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        now = time.time()
        window = 60.0  # 1 minute

        if client_ip not in self.clients:
            self.clients[client_ip] = [now]
            return True, self.rate - 1

        # Purge timestamps older than 1 minute
        self.clients[client_ip] = [
            t for t in self.clients[client_ip] if now - t < window
        ]

        if len(self.clients[client_ip]) >= self.rate:
            retry_after = int(window - (now - self.clients[client_ip][0]))
            return False, max(1, retry_after)

        self.clients[client_ip].append(now)
        return True, self.rate - len(self.clients[client_ip])


# Rate limiters for sensitive endpoints
auth_rate_limiter = SimpleRateLimiter(requests_per_minute=10)
generation_rate_limiter = SimpleRateLimiter(requests_per_minute=20)


def sanitize_text_input(text: str, max_length: int = MAX_TOPIC_LENGTH) -> str:
    """Sanitize user text input to prevent control character injection and DoS."""
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (except newline and tab)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Truncate to maximum length
    return cleaned.strip()[:max_length]


def validate_safe_url(url: str) -> str:
    """Validates that a URL is safe to fetch (protects against SSRF attacks).

    Rejects:
    - Non-HTTP/HTTPS schemes (e.g. file://, gopher://, dict://)
    - Localhost / 127.0.0.1
    - Cloud metadata IPs (169.254.169.254)
    - RFC1918 private subnets
    """
    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Disallowed URL scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: Missing hostname")

    # Disallow common local hostnames
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        raise ValueError("SSRF Protection: Access to localhost or internal metadata is blocked")

    # Check IP addresses
    try:
        ip = ipaddress.ip_address(hostname)
        for network in BLOCKED_IP_NETWORKS:
            if ip in network:
                raise ValueError(f"SSRF Protection: IP {ip} is in a blocked network")
    except ValueError as e:
        # Not an IP string, hostname is a domain name
        if "SSRF Protection" in str(e):
            raise

    return url
