"""Unit tests for API middleware — logging IP extraction and rate limiting.

T034: Proxy-aware IP logic, rate limit enforcement, and header injection.
"""

from unittest.mock import MagicMock

from api.middleware.logging import RequestLoggingMiddleware
from api.middleware.rate_limit import RateLimitMiddleware


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_request(
    client_host: str = "1.2.3.4",
    xff: str | None = None,
    xri: str | None = None,
) -> MagicMock:
    """Build a minimal mock Starlette Request."""
    req = MagicMock()
    req.client = MagicMock()
    req.client.host = client_host

    headers = {}
    if xff:
        headers["x-forwarded-for"] = xff
    if xri:
        headers["x-real-ip"] = xri

    req.headers = headers
    return req


def _logging_middleware(trusted_ips: str = "127.0.0.1,::1") -> RequestLoggingMiddleware:
    """Return a RequestLoggingMiddleware with custom trusted IPs (no real app)."""
    app = MagicMock()
    import os
    original = os.environ.get("TRUSTED_PROXY_IPS")
    os.environ["TRUSTED_PROXY_IPS"] = trusted_ips
    m = RequestLoggingMiddleware(app)
    if original is None:
        os.environ.pop("TRUSTED_PROXY_IPS", None)
    else:
        os.environ["TRUSTED_PROXY_IPS"] = original
    return m


def _rate_limit_middleware(rpm: int = 5) -> RateLimitMiddleware:
    app = MagicMock()
    import os
    original = os.environ.get("TRUSTED_PROXY_IPS")
    os.environ["TRUSTED_PROXY_IPS"] = "10.0.0.1"
    m = RateLimitMiddleware(app, requests_per_minute=rpm)
    if original is None:
        os.environ.pop("TRUSTED_PROXY_IPS", None)
    else:
        os.environ["TRUSTED_PROXY_IPS"] = original
    return m


# ---------------------------------------------------------------------------
# Logging middleware — _get_client_ip
# ---------------------------------------------------------------------------


class TestLoggingMiddlewareClientIp:
    def test_direct_ip_when_not_trusted_proxy(self):
        m = _logging_middleware("127.0.0.1")
        req = _mock_request(client_host="8.8.8.8", xff="1.1.1.1")
        # 8.8.8.8 is not in trusted_proxy_ips → XFF ignored
        assert m._get_client_ip(req) == "8.8.8.8"

    def test_xff_used_when_direct_ip_is_trusted(self):
        m = _logging_middleware("127.0.0.1")
        req = _mock_request(client_host="127.0.0.1", xff="203.0.113.5")
        assert m._get_client_ip(req) == "203.0.113.5"

    def test_xff_first_entry_used_for_chain(self):
        m = _logging_middleware("127.0.0.1")
        req = _mock_request(client_host="127.0.0.1", xff="10.10.10.1, 10.10.10.2")
        assert m._get_client_ip(req) == "10.10.10.1"

    def test_x_real_ip_used_when_xff_absent(self):
        m = _logging_middleware("127.0.0.1")
        req = _mock_request(client_host="127.0.0.1", xri="192.168.1.99")
        assert m._get_client_ip(req) == "192.168.1.99"

    def test_invalid_xff_falls_back_to_direct_ip(self):
        m = _logging_middleware("127.0.0.1")
        req = _mock_request(client_host="127.0.0.1", xff="not-an-ip")
        # XFF is invalid → fall through to direct
        result = m._get_client_ip(req)
        assert result == "127.0.0.1"

    def test_unknown_when_no_client(self):
        m = _logging_middleware("127.0.0.1")
        req = MagicMock()
        req.client = None
        req.headers = {}
        assert m._get_client_ip(req) == "unknown"


# ---------------------------------------------------------------------------
# Rate limit middleware — _get_client_ip (mirrors logging logic)
# ---------------------------------------------------------------------------


class TestRateLimitMiddlewareClientIp:
    def test_direct_ip_when_not_proxy(self):
        m = _rate_limit_middleware()
        req = _mock_request(client_host="5.5.5.5", xff="1.1.1.1")
        # trusted proxy is 10.0.0.1; 5.5.5.5 is untrusted
        assert m._get_client_ip(req) == "5.5.5.5"

    def test_xff_when_trusted_proxy(self):
        m = _rate_limit_middleware()
        req = _mock_request(client_host="10.0.0.1", xff="203.0.113.7")
        assert m._get_client_ip(req) == "203.0.113.7"

    def test_real_ip_when_trusted_proxy_no_xff(self):
        m = _rate_limit_middleware()
        req = _mock_request(client_host="10.0.0.1", xri="203.0.113.8")
        assert m._get_client_ip(req) == "203.0.113.8"


# ---------------------------------------------------------------------------
# Rate limit middleware — sliding window enforcement
# ---------------------------------------------------------------------------


class TestRateLimitEnforcement:
    def test_count_increments_per_request(self):
        m = _rate_limit_middleware(rpm=10)
        # Directly exercise internal counter logic
        import time
        now = time.time()
        m.request_counts["1.2.3.4"] = [(now, 1)] * 9
        m.last_seen["1.2.3.4"] = now
        count = m._get_request_count("1.2.3.4")
        assert count == 9

    def test_old_entries_cleaned_up(self):
        m = _rate_limit_middleware(rpm=10)
        import time
        old = time.time() - 120  # 2 minutes ago
        m.request_counts["1.2.3.4"] = [(old, 1)] * 5
        m.last_seen["1.2.3.4"] = old
        m._cleanup_old_entries("1.2.3.4", time.time())
        assert "1.2.3.4" not in m.request_counts

    def test_evict_stale_clients_removes_old(self):
        m = _rate_limit_middleware(rpm=10)
        import time
        stale = time.time() - 120
        m.last_seen["stale-client"] = stale
        m.request_counts["stale-client"] = []
        m._evict_stale_clients(time.time())
        assert "stale-client" not in m.last_seen

    def test_normalize_ip_valid(self):
        m = _rate_limit_middleware()
        assert m._normalize_ip("192.168.1.1") == "192.168.1.1"

    def test_normalize_ip_invalid_returns_none(self):
        m = _rate_limit_middleware()
        assert m._normalize_ip("not-valid") is None

    def test_normalize_ip_none_returns_none(self):
        m = _rate_limit_middleware()
        assert m._normalize_ip(None) is None
