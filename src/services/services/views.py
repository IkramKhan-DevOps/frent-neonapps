from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from src.services.services.filters import ServiceFilter
from src.services.services.models import Service, ServiceAvailability


class ServicesListView(ListView):
    model = Service

    def get_context_data(self, **kwargs):
        context = super(ServicesListView, self).get_context_data(**kwargs)
        service_filter = ServiceFilter(self.request.GET, queryset=self.get_queryset())
        context['service_filter_form'] = service_filter.form
        paginator = Paginator(service_filter.qs, 30)
        page_number = self.request.GET.get('page')
        user_page_object = paginator.get_page(page_number)
        context['object_list'] = user_page_object
        return context


class ServiceDetailView(DetailView):
    model = Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object
        availability_slots = ServiceAvailability.objects.filter(service=service, is_active=True).order_by('day_of_week', 'start_time')
        context['availability_slots'] = availability_slots
        return context
