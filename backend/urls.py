from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/org/', include('org.urls')),
    path('api/assets/', include('assets.urls')),
    path('api/allocations/', include('allocations.urls')),
    path('api/bookings/', include('booking.urls')),
    path('api/maintenance/', include('maintenance.urls')),
    path('api/audits/', include('audits.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
