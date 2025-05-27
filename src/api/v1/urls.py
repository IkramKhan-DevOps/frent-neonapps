from django.urls import path
from src.api.v1.views import (HomeAPIView, CategorySubRegionProvinceLanguageApiView, ServiceCategoryListAPIView)

app_name = 'v1'

urlpatterns = [
    path('home/', HomeAPIView.as_view(), name='home'),
    path('helpers/', CategorySubRegionProvinceLanguageApiView.as_view(), name='service-helper'),
    path('service-category/', ServiceCategoryListAPIView.as_view(), name='service-categories'),
]
