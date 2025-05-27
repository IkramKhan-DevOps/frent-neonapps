# views.py
from cities_light.models import Region, SubRegion
from django.db import models
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView

from src.services.services.models import Service, ServiceCategory
from .serializers import (
    ServiceHomeListSerializer,
    ServiceCategorySerializer, SubRegionSerializer, RegionSerializer, LanguageSerializer, CountrySerializer,
    ServiceCategoryListSerializer
)
from ...core.models import Language, Country


class HomeAPIView(ListAPIView):
    serializer_class = ServiceHomeListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        popular_services = (
            Service.objects.filter(is_active=True)
            .annotate(
                average_rating=Avg('reviews__rating', filter=models.Q(reviews__is_active=True)),
                reviews_count=Count('reviews', filter=models.Q(reviews__is_active=True))
            )
            .order_by('-average_rating')[:5]
        )
        my_interest = Service.objects.filter(is_active=True).order_by('?')[:10]
        top_categories = ServiceCategory.objects.filter(is_active=True)[:10]

        data = {
            'top_categories': top_categories,
            'my_interest': my_interest,
            'popular_services': popular_services,
            'for_you': my_interest,
            'near_you': my_interest,

        }
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


"""-------------------Helper-------------------"""


class ServiceCategoryListAPIView(ListAPIView):
    serializer_class = ServiceCategoryListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ServiceCategory.objects.filter(is_active=True).order_by('name')


class CategorySubRegionProvinceLanguageApiView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        category = ServiceCategory.objects.all()
        sub_region = SubRegion.objects.all()
        province = Region.objects.all()
        language = Language.objects.all()
        country = Country.objects.all()
        context = {
            'country': CountrySerializer(country, many=True).data,
            'category': ServiceCategorySerializer(category, many=True).data,
            'sub_region': SubRegionSerializer(sub_region, many=True).data,
            'province': RegionSerializer(province, many=True).data,
            'language': LanguageSerializer(language, many=True).data

        }
        return Response(data=context, status=status.HTTP_200_OK)
