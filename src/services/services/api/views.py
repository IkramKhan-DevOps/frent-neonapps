from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, \
    get_object_or_404, CreateAPIView, DestroyAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response

from src.services.services.api.filters import ServiceFilter
from src.services.services.api.serializers import ServiceSerializer, ServiceDetailSerializer, \
    ServiceCreateUpdateSerializer, ServiceImageSerializer, ServiceAvailabilitySerializer, ServiceLocationSerializer, \
    ServiceReviewSerializer, ServiceCurrencySerializer, ServiceLanguageSerializer, \
    ServiceRuleInstructionCreateSerializer, ServiceLanguageCreateSerializer
from src.services.services.models import Service, ServiceImage, ServiceLocation, ServiceAvailability, ServiceReview, \
    ServiceCurrency, ServiceRuleInstruction, ServiceLanguage, ServiceRule

"""SERVICE SEEKER APIS"""


class ServiceListAPIView(ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServiceDetailAPIView(RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(Service, is_active=True, pk=self.kwargs.get('pk'))


"""SERVICE SEEKER APIS"""


# Provider Service
class ProviderServiceListCreateAPIView(ListCreateAPIView):
    queryset = Service.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ServiceCreateUpdateSerializer
        return ServiceSerializer

    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class ProviderServiceRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceDetailSerializer
        return ServiceCreateUpdateSerializer

    def get_object(self):
        return get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Service deleted successfully'})


# Provider Service Image
class ProviderServiceImageUploadCreateAPIView(CreateAPIView):
    queryset = ServiceImage.objects.all()
    serializer_class = ServiceImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = get_object_or_404(Service.objects.filter(provider=self.request.user),
                                    pk=self.kwargs.get('service_pk'))
        serializer.save(service=service)
        return Response(status=status.HTTP_201_CREATED, data={'message': 'Image uploaded successfully'})


class ProviderServiceImageDeleteAPIView(DestroyAPIView):
    queryset = ServiceImage.objects.all()
    serializer_class = ServiceImage
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(ServiceImage, service__provider=self.request.user, pk=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Image deleted successfully'})


# Provider Service Availability
class ServiceAvailabilityCreateAPIView(CreateAPIView):
    queryset = ServiceAvailability.objects.all()
    serializer_class = ServiceAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('service_pk'))
        serializer.save(service=service)


class ServiceAvailabilityUpdateDestroyAPIView(UpdateAPIView, DestroyAPIView):
    queryset = ServiceAvailability.objects.all()
    serializer_class = ServiceAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        service = get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('service_pk'))
        return get_object_or_404(ServiceAvailability, service=service, pk=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Availability slot deleted successfully'})


# Provider Service Location

class ServiceLocationCreateAPIView(CreateAPIView):
    queryset = ServiceLocation.objects.all()
    serializer_class = ServiceLocationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('service_pk'))
        serializer.save(service=service)


class ServiceLocationUpdateDestroyAPIView(UpdateAPIView, DestroyAPIView):
    queryset = ServiceLocation.objects.all()
    serializer_class = ServiceLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        service = get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('service_pk'))
        return get_object_or_404(ServiceLocation, service=service, pk=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Location deleted successfully'})


class ServiceCurrencyView(ListAPIView):
    queryset = ServiceCurrency.objects.all()
    serializer_class = ServiceCurrencySerializer


class ServiceReviewCreateAPIView(CreateAPIView):
    queryset = ServiceReview.objects.all()
    serializer_class = ServiceReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = get_object_or_404(Service, pk=self.kwargs.get('service_pk'))
        serializer.save(service=service, reviewer=self.request.user)


class ServiceLanguageCreateAPIView(CreateAPIView):
    queryset = ServiceLanguage.objects.all()
    serializer_class = ServiceLanguageCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        service = get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('service_pk'))
        language = apps.get_model('core', 'Language').objects.get(pk=request.data.get('language'))
        service_language = ServiceLanguage.objects.filter(service=service, language=language).filter()
        if service_language.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Language already exists'})
        service_language = ServiceLanguage.objects.create(service=service, language=language)
        serializer = ServiceLanguageSerializer(service_language)
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)


class ServiceLanguageDestroyAPIView(DestroyAPIView):
    queryset = ServiceLanguage.objects.all()
    serializer_class = ServiceLanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(ServiceLanguage, pk=self.kwargs.get('pk'),
                                 service_id=self.kwargs.get('service_pk'),
                                 service__provider=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Language deleted successfully'})


class ServiceRuleInstructionCreateAPIView(CreateAPIView):
    """
    API view to create a Service Rule with multiple required materials.
    """
    queryset = ServiceRule.objects.all()
    serializer_class = ServiceRuleInstructionCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service = get_object_or_404(Service, provider=self.request.user, pk=self.kwargs.get('service_pk'))
        event_rule = serializer.validated_data.get('event_rule')
        service_rule = ServiceRule.objects.create(service=service, event_rule=event_rule)
        for material in serializer.validated_data.get('required_material'):
            ServiceRuleInstruction.objects.create(service_rule=service_rule, required_material=material)
        return Response(status=status.HTTP_201_CREATED, data={'message': 'Service rule created successfully'})
