import django_filters
from django.forms import TextInput
from .models import Service

class ServiceFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        widget=TextInput(attrs={'placeholder': 'Service title'}),
        lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        widget=TextInput(attrs={'placeholder': 'Category name'}),
        field_name='category__name',
        lookup_expr='icontains'
    )


    class Meta:
        model = Service
        fields = {}
