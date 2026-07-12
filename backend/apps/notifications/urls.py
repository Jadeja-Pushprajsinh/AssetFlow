from django.urls import path
from apps.notifications import views

urlpatterns = [
    path("",                     views.NotificationListView.as_view(),        name="notification_list"),
    path("unread-count/",        views.UnreadCountView.as_view(),              name="unread_count"),
    path("mark-all-read/",       views.NotificationMarkAllReadView.as_view(),  name="mark_all_read"),
    path("<int:pk>/read/",       views.NotificationMarkReadView.as_view(),     name="mark_read"),
    path("activity/",            views.ActivityLogListView.as_view(),          name="activity_log"),
]
