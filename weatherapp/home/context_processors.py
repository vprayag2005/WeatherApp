def user_settings(request):
    return {"user_settings": getattr(request, "user_settings", None)}
