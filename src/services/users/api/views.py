from django.apps import apps
from django.views.generic import DeleteView
from rest_framework import status
from rest_framework.generics import UpdateAPIView, CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, \
    get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from src.services.services.models import FavoriteService
from src.services.users.api.serializers import UserSerializer, UserImageSerializer, UserAddressSerializer, \
    ServiceProviderDetailSerializer, ServiceProviderSerializer, SocialMediaSerializer, InterestSerializer, \
    CertificationSerializer, UserUpdateSerializer, ServiceProviderLanguageSerializer, FavoriteServiceSerializer, \
    FavoriteServiceCreateSerializer, UserContactSerializer, UserDetailSerializer, UserBlockSerializer, \
    ReportingSerializer
from src.services.users.models import UserImage, User, ServiceProvider, SocialMedia, Interest, Certification, \
    ServiceProviderLanguage, UserContact, Address, BlockedUser

""" ---------------------SERVICE SEEKER APIS------------------------ """


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update user profile
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailSerializer
        return UserUpdateSerializer

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()


class UserRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve user profile
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs.get('pk'))


class UserImageCreateAPIView(CreateAPIView):
    """
    Create user image
    """
    queryset = UserImage.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserImageDestroyAPIView(DestroyAPIView):
    """
    Delete user image
    """
    queryset = UserImage.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Image deleted successfully'})


class UserAddressRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update user address
    """
    queryset = Address.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user_address, created = Address.objects.get_or_create(user=user)
        return user_address

    def perform_update(self, serializer):
        serializer.save()


""" ---------------------SERVICE PROVIDER APIS------------------------ """


class ServiceProviderRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update service provider profile
    """
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceProviderDetailSerializer
        return ServiceProviderSerializer

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.request.user.get_service_provider_profile().id)


class ServiceProviderRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve and update service provider profile
    """
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs.get('pk'))


class ServiceProviderLanguageCreateAPIView(CreateAPIView):
    """
    Create service provider language
    """
    queryset = ServiceProviderLanguage.objects.all()
    serializer_class = ServiceProviderLanguageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(service_provider=self.request.user.get_service_provider_profile())


class ServiceProviderInterestCreateAPIView(CreateAPIView):
    """
    Create service provider interest
    """
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(service_provider=self.request.user.get_service_provider_profile())


class ServiceProviderInterestDestroyAPIView(DestroyAPIView):
    """
    Delete service provider Interest
    """

    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, service_provider=self.request.user.get_service_provider_profile(),
                                 pk=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Interest'
                                                                    ' deleted successfully'})


class ServiceProviderLanguageDestroyAPIView(DestroyAPIView):
    """
    Delete service provider language
    """
    queryset = ServiceProviderLanguage.objects.all()
    serializer_class = ServiceProviderLanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, service_provider=self.request.user.get_service_provider_profile(),
                                 id=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Language deleted successfully'})


class ServiceProviderCertificationCreateAPIView(CreateAPIView):
    """
    Create service provider certification
    """
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(service_provider=self.request.user.get_service_provider_profile())


class ServiceProviderCertificateDestroyAPIView(DestroyAPIView):
    """
    Delete service provider certification
    """
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, service_provider=self.request.user.get_service_provider_profile(),
                                 id=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Certificate deleted successfully'})


class ServiceProviderSocialMediaUpdateAPIView(UpdateAPIView):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, service_provider=self.request.user.get_service_provider_profile())


# User Favorite Service

class FavoriteServiceListCreateAPIView(ListCreateAPIView):
    queryset = FavoriteService.objects.all()
    serializer_class = FavoriteServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FavoriteServiceSerializer
        return FavoriteServiceCreateSerializer

    def get_queryset(self):
        return FavoriteService.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteServiceDestroyAPIView(DestroyAPIView):
    queryset = FavoriteService.objects.all()
    serializer_class = FavoriteServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, user=self.request.user, id=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Favorite service deleted successfully'})


class UserContactListCreateAPIView(ListCreateAPIView):
    queryset = UserContact.objects.all()
    serializer_class = UserContactSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return UserContact.objects.filter(user=self.request.user)


class UserContactUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = UserContact.objects.all()
    serializer_class = UserContactSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, user=self.request.user, id=self.kwargs.get('pk'))

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'Contact deleted successfully'})


class BlockedUserListCreateAPIView(ListCreateAPIView):
    queryset = BlockedUser.objects.all()
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.blocked_users.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BlockedUserDestroyAPIView(DestroyAPIView):
    queryset = BlockedUser.objects.all()
    serializer_class = UserBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(self.queryset, user=self.request.user, id=self.kwargs.get('pk'))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK, data={'message': 'User unblocked successfully'})


class ReportListCreateApiView(ListCreateAPIView):
    report = apps.get_model('reporting', 'Report')
    serializer_class = ReportingSerializer
    queryset = report.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(reported_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
