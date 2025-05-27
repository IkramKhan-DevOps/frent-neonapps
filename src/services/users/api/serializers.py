from django.apps import apps
from rest_framework import serializers

from src.api.v1.serializers import LanguageSerializer
from src.core.models import Language
from src.services.services.api.serializers import ServiceSerializer
from src.services.services.models import FavoriteService
from src.services.users.models import UserImage, Address, Interest, Certification, SocialMedia, User, ServiceProvider, \
    ServiceProviderLanguage, UserContact, BlockedUser


# """ ---------------------User Serializers--------------------- """

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        service_review = apps.get_model('services', 'ServiceReview')
        model = service_review
        fields = ['id', 'service_title', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'service_title', 'rating', 'comment', 'created_at']


class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        service = apps.get_model('services', 'Service')
        model = service
        fields = ['id', 'title', 'provider', 'thumbnail', 'service_type', 'description',
                  'price_type', 'price', 'discount', 'is_active']


class UserSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_image', 'bio', 'images',
                  'date_joined', 'last_login', ]
        read_only_fields = ['username', 'email', 'date_joined', 'images', 'last_login']

    def get_images(self, obj):
        images = obj.images.all()
        return UserImageSerializer(images, many=True).data


class UserReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer()

    class Meta:
        service_review = apps.get_model('services', 'ServiceReview')
        model = service_review
        fields = ['id', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['reviewer', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    given_reviews = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_image', 'bio', 'images',
                  'given_reviews',
                  'date_joined', 'last_login', ]
        read_only_fields = ['username', 'email', 'date_joined', 'images', 'last_login']

    def get_images(self, obj):
        images = obj.images.all()
        return UserImageSerializer(images, many=True).data

    def get_given_reviews(self, obj):
        reviews = obj.received_reviews.all()
        return UserReviewSerializer(reviews, many=True).data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_image', 'bio', ]


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ['id', 'image']


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'address', 'city', 'region', 'country', 'zip_code', ]
        read_only_fields = ['user']


# """ ---------------------Service Provider Interest  Serializers--------------------- """
class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']


# """ ---------------------Service Provider Language Serializers--------------------- """
class ServiceProviderLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderLanguage
        fields = ['id', 'language', 'fluency']


class ServiceProviderLanguageDetailSerializer(ServiceProviderLanguageSerializer):
    language = LanguageSerializer()

    class Meta(ServiceProviderLanguageSerializer.Meta):
        pass


# """ ---------------------Service Provider Certificate Serializers--------------------- """

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'certificate_file', ]


# """ ---------------------Service Provider Social Media Serializers--------------------- """
class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'platform', 'url']


# """ ---------------------Service Provider Serializers--------------------- """

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['id', 'company_name', 'phone_number', 'website', 'verified']


class ServiceProviderDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    social_media = SocialMediaSerializer()
    interests = InterestSerializer(many=True)
    certifications = CertificationSerializer(many=True)
    languages = ServiceProviderLanguageDetailSerializer(many=True)
    services = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    address = UserAddressSerializer(source="user.address")

    class Meta:
        model = ServiceProvider
        fields = ['id', 'user', 'address', 'company_name', 'phone_number', 'website', 'rating', 'total_reviews',
                  'verified', 'status', 'social_media', 'interests', 'certifications', 'languages', 'reviews',
                  'services']
        read_only_fields = ['user', 'social_media', 'interests', 'certifications', 'address', 'rating', 'total_reviews',
                            'verified', 'status', ]

    def get_reviews(self, obj):
        reviews = obj.user.provider_reviews.all()
        return ReviewSerializer(reviews, many=True).data

    def get_services(self, obj):
        services = obj.user.services.all()
        return ServiceListSerializer(services, many=True).data


# """ ---------------------Favorite Service Serializers--------------------- """
class FavoriteServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = FavoriteService
        fields = ['id', 'user', 'service']


class FavoriteServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteService
        fields = ['id', 'service']

    def validate(self, attrs):
        if FavoriteService.objects.filter(user=self.context['request'].user, service=attrs['service']).exists():
            raise serializers.ValidationError("Service already added to favorites")
        return attrs


# """ ---------------------User Contact Serializers--------------------- """
class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContact
        fields = ['id', 'name', 'phone_number']


# """ ---------------------User Block and Report Serializers--------------------- """
class UserBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = ['id', 'blocked_user', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_blocked_user(self, blocked_user):
        """Ensure the user is not blocking the same user again."""
        user = self.context['request'].user
        if BlockedUser.objects.filter(user=user, blocked_user=blocked_user).exists():
            raise serializers.ValidationError("You have already blocked this user.")
        return blocked_user


report = apps.get_model('reporting', 'Report')


class ReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = report
        fields = ['id', 'report_type', 'reported_user', 'reported_service', 'reason', 'additional_info', 'is_resolved',
                  'resolved_at']
        read_only_fields = ['id', 'is_resolved', 'resolved_at']

    def validate_reported_user(self, reported_user):
        user = self.context['request'].user
        if report.objects.filter(reported_user=reported_user, reported_by=user).exists():
            raise serializers.ValidationError("You have already reported this.")
        return reported_user
