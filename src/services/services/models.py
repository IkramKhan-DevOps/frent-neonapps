import uuid

from cities_light.models import City, Region, Country
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field

from src.services.users.models import User, ServiceProvider


class ServiceCategory(models.Model):
    """Service Category Model"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True, help_text="Unique category name.")
    thumbnail = models.ImageField(upload_to='services/categories/', null=True, blank=True,
                                  help_text='Recommended size: 250x250.')
    description = models.TextField(blank=True, null=True, help_text="Small description of the category.")
    is_active = models.BooleanField(default=True, help_text="Indicates if the category is currently active.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name'], name="unique_service_category_name")
        ]


class ServiceCurrency(models.Model):
    """Service Currency Model"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True, help_text="Unique currency name.")
    code = models.CharField(max_length=3, unique=True, help_text="Unique currency code.")
    symbol = models.CharField(max_length=5, unique=True, help_text="Unique currency symbol.")
    description = models.TextField(blank=True, null=True, help_text="Small description of the currency.")
    is_active = models.BooleanField(default=True, help_text="Indicates if the currency is currently active.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Currencies"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name'], name="unique_service_currency_name")
        ]


class Service(models.Model):
    PRICE_TYPE_CHOICES = [
        ('fixed', 'Fixed'),
        ('hourly', 'Hourly'),
    ]
    SERVICE_TYPE_CHOICES = [
        ('onside', 'Onsite'),
        ('online', 'Online'),
        ('both', 'Both'),
    ]

    """Represents a service provided by service providers"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=255, help_text="Service title (max 255 characters).")
    slug = models.SlugField(max_length=255, unique=True, help_text="Unique slug for the service.")
    thumbnail = models.ImageField(upload_to='services/thumbnails/', null=True, blank=True,
                                  help_text='Recommended size: 250x250.')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='services', help_text="The category this service belongs to.")
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES, default='onside',
                                    help_text="The type of service (onsite, online, or both).")
    description = models.TextField(null=True, blank=True, help_text="Small description for your project")
    content = CKEditor5Field(
        'Text', config_name='extends', null=True, blank=True, help_text="Full description for your project"
    )

    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES, default='fixed',
                                  help_text="The type of pricing for the service.")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)],
                                help_text="Service price (up to 10 digits and 2 decimal places).")
    currency = models.ForeignKey(ServiceCurrency, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='services',
                                 help_text="The currency for the service price(e.g.,Lira, USD, EUR, etc.).")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                   validators=[MinValueValidator(0.00), MaxValueValidator(99.00)]
                                   )

    is_active = models.BooleanField(default=True, help_text="Indicates if the service is available for booking.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.provider.username}"

    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(fields=['provider', 'title'], name="unique_service_per_provider")
        ]

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)
        category_slug = slugify(self.category.name) if self.category else ''
        provider_slug = slugify(self.provider.username)
        self.slug = '-'.join(filter(None, [base_slug, category_slug, provider_slug]))

        # Ensure the slug is unique
        if Service.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{uuid.uuid4().hex[:5]}"

        super().save(*args, **kwargs)

    def get_discounted_price(self):
        return round(self.price - (self.price * (self.discount / 100)), 2)

    def get_total_rating(self):
        reviews = self.reviews.filter(is_active=True)
        total_rating = sum([review.rating for review in reviews])
        return total_rating

    def get_service_schedule(self):
        return self.availability_slots.filter(is_active=True)


class ServiceImage(models.Model):
    """Service Image Model"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/images/', help_text='Recommended size: 800x600.')
    is_active = models.BooleanField(default=True, help_text="Indicates if the service is available for booking.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.service.title}"


class ServiceAvailability(models.Model):
    """Service availability slots for providers"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability_slots')

    day_of_week = models.CharField(max_length=10, help_text="Day of the week (e.g., Monday).")
    start_time = models.TimeField(help_text="Start time of availability.")
    end_time = models.TimeField(help_text="End time of availability.")
    timezone = models.CharField(max_length=50, default="UTC",
                                help_text="Timezone for the availability slot.")  # New attribute

    is_active = models.BooleanField(default=True, help_text="Is this availability slot active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Service Availabilities"
        ordering = ['day_of_week', 'start_time']
        constraints = [
            models.UniqueConstraint(fields=['service', 'day_of_week', 'start_time'], name="unique_service_availability")
        ]

    def __str__(self):
        return f"{self.service.title} available on {self.day_of_week} from {self.start_time} to {self.end_time}"


class ServiceLocation(models.Model):
    """Service location for providers"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='location')
    address = models.CharField(max_length=255, help_text="Service location address.")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_locations")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="service_locations")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="service_locations")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                   help_text="Latitude of the service location.")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                    help_text="Longitude of the service location.")
    is_active = models.BooleanField(default=True, help_text="Is this service location active?")

    class Meta:
        verbose_name_plural = "Service Locations"
        ordering = ['city', 'region', 'country']

    def __str__(self):
        return f"{self.service.title} located at {self.address}, {self.city}, {self.region}, {self.country}"


class ServiceReview(models.Model):
    """Stores reviews for services"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Rating (1-5).")
    comment = models.TextField(blank=True, null=True, help_text="Optional review comment.")
    is_active = models.BooleanField(default=True, help_text="Is this ServiceReview active?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.service.title} by {self.reviewer.username}"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['service', 'reviewer'], name="unique_service_review_per_user")
        ]


class ServicePurchasing(models.Model):
    """Tracks requests made for services"""
    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'Paypal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('full', 'Full Payment'),
        ('partial', 'Partial Payment'),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='requests')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, null=True, blank=False,
                                      help_text="Payment method used for the service request.")
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, default='full',
                                    help_text="Payment type for the service request.")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)],
                                 help_text="Service request amount (up to 10 digits and 2 decimal places).")
    currency = models.ForeignKey(ServiceCurrency, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='service_requests',
                                 help_text="The currency for the service request amount.")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                   validators=[MinValueValidator(0.00), MaxValueValidator(99.00)]
                                   )
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')

    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False, help_text="Indicates if the service request has been paid.")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes for the request.")

    def __str__(self):
        return f"{self.seeker.username}'s request for {self.service.title}"

    class Meta:
        ordering = ['-requested_at']
        constraints = [
            models.UniqueConstraint(fields=['seeker', 'service'], name="unique_service_request_per_user")
        ]


class FavoriteService(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        help_text="The user who added the service to their favorites."
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='favorited_by',
        help_text="The service that was added to favorites."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'service')
        ordering = ['-created_at']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f"{self.user.username} favorited {self.service.title}"
