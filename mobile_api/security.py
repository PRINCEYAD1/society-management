import time

from django.core.cache import cache
from django.http import JsonResponse


class MobileLoginRateLimitMiddleware:
    """Simple IP-based rate limiter for the mobile login endpoint.

    This is intentionally conservative and dependency-free. It reduces
    brute-force attempts without affecting normal authenticated API traffic.
    For multi-instance production deployments, configure a shared cache
    backend (for example Redis) so counters are shared across instances.
    """

    LOGIN_PATH = "/api/auth/login/"
    WINDOW_SECONDS = 15 * 60
    MAX_ATTEMPTS = 10

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path == self.LOGIN_PATH:
            client_ip = self._client_ip(request)
            key = f"mobile-login-rate:{client_ip}"
            record = cache.get(key)
            now = int(time.time())

            if not isinstance(record, dict):
                record = {"count": 0, "started": now}

            started = int(record.get("started", now))
            count = int(record.get("count", 0))

            if now - started >= self.WINDOW_SECONDS:
                started = now
                count = 0

            if count >= self.MAX_ATTEMPTS:
                retry_after = max(
                    1,
                    self.WINDOW_SECONDS - (now - started),
                )
                response = JsonResponse(
                    {
                        "success": False,
                        "message": (
                            "Too many login attempts. "
                            "Please wait before trying again."
                        ),
                    },
                    status=429,
                )
                response["Retry-After"] = str(retry_after)
                return response

            cache.set(
                key,
                {"count": count + 1, "started": started},
                timeout=self.WINDOW_SECONDS,
            )

        return self.get_response(request)

    @staticmethod
    def _client_ip(request):
        # Render/Django may receive X-Forwarded-For from a trusted proxy.
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
