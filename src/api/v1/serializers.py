# serializers.py
from cities_light.models import SubRegion, Region, Country
from rest_framework import serializers
from src.core.models import Language, Country
from src.core.models import Country as GlobalCountry
from src.services.services.api.serializers import UserProfileSerializer
from src.services.services.models import ServiceCategory, Service, \
    ServiceCurrency

""" ---------------------Helper Serializers--------------------- """


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalCountry
        fields = ['id', 'name']


class CityLightCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class RegionSerializer(serializers.ModelSerializer):
    country = CityLightCountrySerializer()

    class Meta:
        model = Region
        fields = ['id', 'name', 'country']


class SubRegionSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = SubRegion
        fields = ['id', 'name', 'region']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'short_name']


class ServiceCategoryListSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'parent', 'thumbnail', 'description', 'is_active', 'subcategories']

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return ServiceCategorySerializer(obj.subcategories.all(), many=True, context=self.context).data
        return []


""" ---------------------Service Serializers--------------------- """


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'thumbnail', 'description', 'is_active']


class ServiceCurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCurrency
        fields = ['id', 'name']


class ServiceHomeSerializer(serializers.ModelSerializer):
    provider = UserProfileSerializer()
    category = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    currency = ServiceCurrency()

    class Meta:
        model = Service
        fields = ['id', 'title', 'thumbnail', 'provider', 'service_type', 'category', 'schedule', 'description',
                  'price_type', 'price', 'discount', 'currency', 'rating',
                  'is_active']

    def get_rating(self, obj):
        return obj.get_total_rating()

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_schedule(self, obj):
        schedules = obj.get_service_schedule()
        data = []
        for schedule in schedules:
            data.append({
                'day_of_week': schedule.day_of_week,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'timezone': schedule.timezone
            })
        return data


class ServiceHomeListSerializer(serializers.Serializer):
    top_categories = ServiceCategorySerializer(many=True)
    my_interest = ServiceHomeSerializer(many=True)
    popular_services = ServiceHomeSerializer(many=True)
    for_you = ServiceHomeSerializer(many=True)
    near_you = ServiceHomeSerializer(many=True)
