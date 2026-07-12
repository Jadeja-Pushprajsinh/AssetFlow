from django.urls import path
from apps.audits.views import AuditsPlaceholderView

urlpatterns = [
    path("", AuditsPlaceholderView.as_view(), name="audits_placeholder"),
]
