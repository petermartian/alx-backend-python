# chats/middleware.py
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.core.handlers.wsgi import WSGIRequest
from typing import Callable, Dict, List


LOG_FILE_PATH = "requests.log"


class RequestLoggingMiddleware:
    """
    Logs each request: 'YYYY-mm-dd HH:MM:SS - User: <user> - Path: <path>'
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        user = request.user.username if getattr(request, "user", None) and request.user.is_authenticated else "Anonymous"
        line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User: {user} - Path: {request.path}\n"
        try:
            with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            # never block the request because of logging errors
            pass

        return self.get_response(request)
    
    class RestrictAccessByTimeMiddleware:
        """
        Deny access outside allowed hours (default: 06:00–21:00 local server time).
        Returns 403 Forbidden with a short message.
        """
        ALLOW_START_HOUR = 6   # 06:00
        ALLOW_END_HOUR = 21    # 21:00

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        now_local = timezone.localtime()
        hour = now_local.hour
        allowed = (self.ALLOW_START_HOUR <= hour < self.ALLOW_END_HOUR)
        if not allowed:
            return HttpResponseForbidden("Access to chat is restricted at this time (allowed 06:00–21:00).")
        return self.get_response(request)
    
    class OffensiveLanguageMiddleware:
        """
        Blocks offensive words in message content and rate-limits POSTs
        to /api/messages/ to 5 per minute per IP.
        """
    WINDOW_SECONDS = 60
    LIMIT = 5
    BANNED = {"spamword", "offensive1", "offensive2"}  # sample list

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        # naive in-memory store: ip -> [timestamps]; OK for assignment/demo
        self._bucket: Dict[str, List[float]] = {}

    def _client_ip(self, request: WSGIRequest) -> str:
        xfwd = request.META.get("HTTP_X_FORWARDED_FOR")
        if xfwd:
            return xfwd.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    def __call__(self, request: WSGIRequest):
        # Only guard message creation endpoints (adjust path as needed)
        if request.method == "POST" and request.path.startswith("/api/messages"):
            # Offensive word check (if JSON field 'content' exists)
            try:
                body = request.body.decode("utf-8") if request.body else ""
                lower = body.lower()
                if any(bad in lower for bad in self.BANNED):
                    return JsonResponse({"detail": "Inappropriate language detected."}, status=403)
            except Exception:
                pass

            # Rate limit per IP
            ip = self._client_ip(request)
            now = datetime.now().timestamp()
            window_start = now - self.WINDOW_SECONDS
            bucket = self._bucket.get(ip, [])
            # drop old timestamps
            bucket = [t for t in bucket if t >= window_start]
            if len(bucket) >= self.LIMIT:
                return JsonResponse({"detail": "Rate limit exceeded: 5 messages per minute."}, status=403)
            bucket.append(now)
            self._bucket[ip] = bucket

        return self.get_response(request)

class RolepermissionMiddleware:
    """
    Allows write actions only for admins or moderators on chat endpoints.
    Read (GET/HEAD/OPTIONS) stays open to authenticated users.
    """
    PROTECTED_PREFIXES = ("/api/messages", "/api/conversations")

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        # Only protect chat API paths
        if request.path.startswith(self.PROTECTED_PREFIXES):
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                user = getattr(request, "user", None)
                is_mod = False
                if user and user.is_authenticated:
                    is_mod = user.is_staff or user.is_superuser or \
                             user.groups.filter(name__in=["moderator", "admin"]).exists()
                if not is_mod:
                    return HttpResponseForbidden("You do not have permission to perform this action.")
        return self.get_response(request)

