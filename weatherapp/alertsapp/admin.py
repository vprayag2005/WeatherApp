from django.contrib import admin

from alertsapp.models import SubdivisionAlert


@admin.register(SubdivisionAlert)
class SubdivisionAlertAdmin(admin.ModelAdmin):
    list_display = (
        "subdivision_name",
        "source_date",
        "source_updated_at",
        "synced_at",
    )
    search_fields = ("subdivision_name", "subdivision_slug")
    ordering = ("subdivision_name",)

