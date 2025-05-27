from django.apps import apps
from rest_framework import serializers

from src.services.services.models import ServiceCategory, Service, ServiceImage, ServiceAvailability, ServiceReview, \
    ServiceCurrency, ServiceLocation, FavoriteService, ServiceLanguage, ServiceRule, ServiceRuleInstruction, UserReview
from src.services.users.models import User

""" ---------------------Helper Serializers--------------------- """


class UserProfileSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'provider_id', 'username', 'profile_image', 'location']

    def get_location(self, obj):
        if obj.get_provider_location():
            return obj.get_provider_location()
        return None

    def get_provider_id(self, obj):
        return obj.get_service_provider_profile().id if obj.get_service_provider_profile() else None


""" ---------------------Service Serializers--------------------- """


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'parent', 'thumbnail', 'description', 'is_active']
        ref_name = 'ServiceCategoryServices'


class ServiceCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCurrency
        fields = ['id', 'name']


class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ['id', 'image']


class ServiceAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAvailability
        fields = ['id', 'repeat_type', 'activity_type', 'day_of_week', 'start_time', 'end_time', 'timezone',
                  'is_active']


class ServiceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLocation
        fields = ['id', 'address', 'city', 'region', 'country', 'latitude', 'longitude']


class ServiceReviewSerializer(serializers.ModelSerializer):
    reviewer = UserProfileSerializer(read_only=True)  # Make reviewer read-only

    class Meta:
        model = ServiceReview
        fields = ['id', 'service', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['service', 'reviewer', 'created_at']

    def validate(self, data):
        if data['rating'] < 1 or data['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return data


class UserServiceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReview
        fields = ['id', 'reviewed_user', 'rating', 'comment', 'created_at']

    def validate(self, data):
        if data['rating'] < 1 or data['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return data


class ServiceSerializer(serializers.ModelSerializer):
    provider = UserProfileSerializer()
    category = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    images = ServiceImageSerializer(many=True, read_only=True)
    currency = ServiceCurrencySerializer()

    class Meta:
        model = Service
        fields = ['id', 'title', 'provider', 'images', 'thumbnail', 'category', 'service_type', 'schedule',
                  'description',
                  'price_type', 'price', 'discount', 'currency', 'rating', 'is_active']

    def get_rating(self, obj):
        return obj.get_total_rating()

    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        return None

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


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        language = apps.get_model('core', 'Language')
        model = language
        fields = ['name', 'short_name']
        ref_name = 'LanguageServices'


class ServiceLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = ServiceLanguage
        fields = ['id', 'language']


class ServiceLanguageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLanguage
        fields = ['id', 'language', 'is_active']
        read_only_fields = ['is_active']


class ServiceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRule
        fields = ['id', 'service', 'event_rule']
        read_only_fields = ['event_rule', 'service']


class ServiceRuleInstructionSerializer(serializers.ModelSerializer):
    service_rule = ServiceRuleSerializer()

    class Meta:
        model = ServiceRuleInstruction
        fields = ['id', 'service_rule', 'required_material', 'created_at', 'updated_at']
        read_only_fields = ['service_rule', 'required_material', 'created_at', 'updated_at']


class ServiceDetailSerializer(serializers.ModelSerializer):
    provider = UserProfileSerializer()
    images = ServiceImageSerializer(many=True, read_only=True)
    category = ServiceCategorySerializer()
    availability_slots = ServiceAvailabilitySerializer(many=True, read_only=True)
    reviews = ServiceReviewSerializer(many=True, read_only=True)
    currency = ServiceCurrencySerializer()
    location = ServiceLocationSerializer(many=True, read_only=True)
    languages = ServiceLanguageSerializer(many=True, read_only=True)
    rules_and_instructions = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'provider', 'service_type', 'thumbnail', 'description', 'content', 'price_type', 'price',
            'discount', 'currency', 'number_of_people',
            'category', 'is_active', 'images', 'availability_slots', 'rules_and_instructions', 'location', 'languages',
            'reviews', 'created_at'
        ]

    def get_rules_and_instructions(self, obj):
        rules = ServiceRule.objects.filter(service=obj)
        data = []
        for rule in rules:
            instructions = ServiceRuleInstruction.objects.filter(service_rule=rule)
            instructions_data = []
            for instruction in instructions:
                instructions_data.append({
                    'required_material': instruction.required_material
                })
            data.append({
                'id': rule.id,
                'event_rule': rule.event_rule,
                'instructions': instructions_data
            })
        return data


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'category', 'service_type', 'thumbnail', 'description', 'content', 'price_type',
                  'price', 'number_of_people',
                  'discount', 'currency', 'is_active']

    def validate_title(self, value):
        request = self.context.get("request")
        if Service.objects.filter(provider=request.user, title=value).exists():
            raise serializers.ValidationError("You already have a service with this title.")
        return value


class ServiceRuleInstructionCreateSerializer(serializers.Serializer):
    """Get Event Rule  and multiple required_material"""
    event_rule = serializers.CharField()
    required_material = serializers.ListField(child=serializers.CharField())
