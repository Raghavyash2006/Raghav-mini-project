from django.contrib import admin

from .admin_site import admin_site
from .models import Feedback, LocalizationJob, LocalizationVariation


@admin.register(LocalizationJob, site=admin_site)
class LocalizationJobAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "source_language", "target_language", "target_region", "tone", "audience", "created_at")
    list_filter = ("user", "source_language", "target_language", "target_region", "tone", "audience", "created_at")
    search_fields = ("source_text", "ocr_text", "user__username", "user__email")


@admin.register(LocalizationVariation, site=admin_site)
class LocalizationVariationAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "variant_name", "cultural_risk_score", "created_at")
    list_filter = ("variant_name", "created_at")
    search_fields = ("localized_text",)


@admin.register(Feedback, site=admin_site)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "variation", "liked", "created_at")
    list_filter = ("liked", "created_at")
