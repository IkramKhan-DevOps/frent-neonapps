import django_filters
from django.db.models import Avg

from src.services.services.models import Service


class ServiceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_services', field_name='search By Title ')
    category = django_filters.UUIDFilter(field_name="category__id")
    average_rating = django_filters.NumberFilter(method='filter_by_average_rating')
    date = django_filters.CharFilter(method='filter_by_date_and_time')
    start_time = django_filters.TimeFilter(method='filter_by_date_and_time')
    end_time = django_filters.TimeFilter(method='filter_by_date_and_time')

    address = django_filters.CharFilter(field_name='location__address', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='location__city', lookup_expr='icontains')
    region = django_filters.CharFilter(field_name='location__region', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='location__country__name', lookup_expr='icontains')

    latitude = django_filters.CharFilter(method='filter_by_latitude')
    longitude = django_filters.CharFilter(method='filter_by_longitude')

    class Meta:
        model = Service
        fields = ['category', 'average_rating', 'date', 'start_time', 'end_time']

    def filter_by_average_rating(self, queryset, name, value):
        return queryset.annotate(average_rating=Avg('reviews__rating')).filter(average_rating=value)

    def filter_by_date_and_time(self, queryset, name, value):
        date = self.data.get('date')
        start_time = self.data.get('start_time')
        end_time = self.data.get('end_time')

        if date and start_time and end_time:
            queryset = queryset.filter(
                availability_slots__day_of_week=date,
                availability_slots__start_time__lte=start_time,
                availability_slots__end_time__gte=end_time,
                availability_slots__is_active=True
            )

        return queryset

    def filter_by_latitude(self, queryset, name, value):
        longitude = self.data.get('longitude')

        if value and longitude:
            return queryset.filter(location__latitude__range=(float(value) - 5, float(value) + 5),
                                   location__longitude__range=(float(longitude) - 5, float(longitude) + 5))
        return queryset

    def filter_by_longitude(self, queryset, name, value):
        latitude = self.data.get('latitude')

        if value and latitude:
            return queryset.filter(location__longitude__range=(float(value) - 5, float(value) + 5),
                                   location__latitude__range=(float(latitude) - 5, float(latitude) + 5))
        return queryset

    def search_services(self, queryset, name, value):
        return queryset.filter(title__icontains=value) | queryset.filter(description__icontains=value)
