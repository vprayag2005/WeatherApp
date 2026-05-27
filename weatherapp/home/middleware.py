from uuid import uuid4

from django.http import JsonResponse
from django.shortcuts import redirect

from home.models import UserSettings


class UserSettingsRequiredMiddleware:
    EXEMPT_PREFIXES = (
        "/settings/",
        "/alerts/",
        "/admin/",
        "/static/",
        "/radar/tiles/",
    )
    EXEMPT_PATHS = {
        "/favicon.ico",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_visitor_id = request.COOKIES.get("visitor_id")
        visitor_id = cookie_visitor_id or uuid4().hex

        request.visitor_id = visitor_id
        request.user_settings = UserSettings.objects.filter(visitor_id=visitor_id).first()

        if request.user_settings is None and not self._is_exempt_path(request.path):
            if self._expects_json(request):
                response = JsonResponse(
                    {"error": "Please complete your settings before using the app."},
                    status=403,
                )
            else:
                response = redirect("settings")
        else:
            response = self.get_response(request)

        if not cookie_visitor_id:
            response.set_cookie(
                "visitor_id",
                visitor_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax",
            )
        return response

    def _is_exempt_path(self, path):
        return path in self.EXEMPT_PATHS or any(
            path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES
        )

    def _expects_json(self, request):
        accept_header = request.headers.get("Accept", "")
        return "application/json" in accept_header or request.path == "/fetch-data/"
