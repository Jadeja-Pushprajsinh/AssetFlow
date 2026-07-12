"""
AssetFlow root URL configuration.
All API endpoints are prefixed with /api/v1/.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/",     include("apps.accounts.urls")),
    path("api/v1/org/",      include("apps.org.urls")),
    path("api/v1/assets/",   include("apps.assets.urls")),
    path("api/v1/allocations/", include("apps.allocations.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),
    path("api/v1/maintenance/", include("apps.maintenance.urls")),
    path("api/v1/audits/",   include("apps.audits.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reports/",  include("apps.reports.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
