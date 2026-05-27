from django.contrib import admin

from home.models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("city", "state", "country", "updated_at")
    search_fields = ("city", "country", "state")
