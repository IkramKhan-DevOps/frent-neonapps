from django.urls import path, include

from src.services.order.views import (
    AdvertisementListView, AdvertisementRequesterListView, OrderListView, OrderDetailView
)

app_name = "order"

urlpatterns = [
    path('advertisement/', AdvertisementListView.as_view(), name='advertisement-list'),
    path('advertisement-request/<str:advertisement_id>/', AdvertisementRequesterListView.as_view(),
         name='advertisement-request-list'),
    path('order/', OrderListView.as_view(), name='order-list'),
    path('order/<str:pk>/', OrderDetailView.as_view(), name='order-detail'),
]

urlpatterns += [
    path('order/api/', include('src.services.order.api.urls', namespace='order-api')),
]
