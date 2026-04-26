from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone


class LocaleForgeAdminSite(admin.AdminSite):
    site_header = "LocaleForge Admin"
    site_title = "LocaleForge Admin"
    index_title = "Platform overview"
    index_template = "admin/localeforge_index.html"

    def index(self, request, extra_context=None):
        user_model = get_user_model()
        today = timezone.localdate()
        stats = {
            "total_users": user_model.objects.count(),
            "active_users": user_model.objects.filter(is_active=True).count(),
            "staff_users": user_model.objects.filter(is_staff=True).count(),
            "localization_jobs": self._job_model().objects.count(),
            "today_jobs": self._job_model().objects.filter(created_at__date=today).count(),
            "recent_users": user_model.objects.annotate(job_count=Count("localization_jobs")).order_by("-last_login", "-date_joined")[:5],
        }
        context = extra_context or {}
        context.update({"site_stats": stats})
        return super().index(request, context)

    def _job_model(self):
        from apps.localization.models import LocalizationJob

        return LocalizationJob


admin_site = LocaleForgeAdminSite(name="localeforge_admin")