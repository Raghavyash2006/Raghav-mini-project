from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from apps.localization.admin_site import admin_site
from apps.localization.views import HomeView, LoginPageView, LogoutPageView, SignupPageView

urlpatterns = [
    path("admin/", admin_site.urls),
    path("auth/login/", LoginPageView.as_view(), name="login"),
    path("auth/signup/", SignupPageView.as_view(), name="signup"),
    path("auth/logout/", LogoutPageView.as_view(), name="logout"),
    path("api/", include("apps.localization.urls")),
    path("", HomeView.as_view(), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
