from django.urls import path

from src.apps.whisper.views import (
    EmailNotificationListView, EmailNotificationRetryView, FCMNotificationCreateAdminView)

app_name = 'whisper'

urlpatterns = [
    path('email/list/', EmailNotificationListView.as_view(), name='emailnotification-list'),
    path('email/<str:pk>/retry/', EmailNotificationRetryView.as_view(), name='emailnotification-retry'),

    path('notification/create/admin/', FCMNotificationCreateAdminView.as_view(), name='device-create-admin'),

]
