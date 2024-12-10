from django.urls import path, include
from .views import (
    ServicesListView, ServiceDetailView
)
app_name = "services"

urlpatterns = [
    path('services/api/', include('src.services.services.api.urls', namespace='services-api')),
    path('service/', ServicesListView.as_view(), name='services-list'),
    path('service/<str:pk>/', ServiceDetailView.as_view(), name='services-detail'),

]
