import random
import uuid

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now
from django_otp.models import Device
from django_resized import ResizedImageField
from phonenumber_field.modelfields import PhoneNumberField

from src.core.models import Country


class User(AbstractUser):
    """Custom User Model to allow switching between ServiceProvider and ServiceSeeker"""
    USER_TYPES = [
        ('admin', 'Admin'),
        ('service_provider', 'Service Provider'),
        ('service_seeker', 'Service Seeker'),
    ]

    username_validator = UnicodeUsernameValidator()
    email = models.EmailField(unique=True, null=True, blank=False, max_length=200)

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )

    profile_image = ResizedImageField(
        upload_to='users/images/profiles/', null=True, blank=True, size=[250, 250], quality=75, force_format='PNG',
        help_text='Profile image must be 250x250 and in PNG format', crop=['middle', 'center']
    )
    bio = models.TextField(blank=True, null=True, help_text="Short description about the user.")
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='service_seeker')
    phone_number = PhoneNumberField(null=True, blank=False, unique=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "phone_number"

    class Meta:
        ordering = ['-id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        """Override save to set user_type for admin users"""
        if self.is_staff:
            self.user_type = 'admin'
        return super(User, self).save(*args, **kwargs)

    def get_service_provider_profile(self):
        """Helper to get the service provider profile if the user is a provider"""
        if hasattr(self, 'service_provider_profile'):
            return self.service_provider_profile
        return None

    def get_user_wallet(self):
        if hasattr(self, 'wallet'):
            return self.wallet
        return None

    def get_provider_location(self):
        """Returns formatted location details from the ServiceProvider model"""
        if hasattr(self, 'address') and self.address.address:
            return f"{self.address.city}, {self.address.region}, {self.address.country.name}"
        return None

    def get_address(self):
        if hasattr(self, 'address'):
            return self.address
        return None

    def is_stripe_connected(self):
        return self.get_user_wallet().is_stripe_connected()

    def is_stripe_account_active(self):
        return self.get_user_wallet().is_stripe_account_active()

    def get_available_balance(self):
        return self.get_user_wallet().get_available_balance()

    def get_pending_balance(self):
        return self.get_user_wallet().get_pending_balance()

    def get_connect_balance(self):
        return self.get_user_wallet().get_connect_balance()

    def bank_account_active(self):
        """Check if the user has an active bank account"""
        return True if self.bank_accounts.filter(is_active=True).first() else False

    def user_registration_completed(self):
        return getattr(self, 'user_registration_otp', False) and self.user_registration_otp.is_verified

    def __str__(self):
        name = self.get_full_name() or self.username or str(self.phone_number)
        return f"User #{self.id} - {name} ({self.user_type})"


class UserRegistrationOTP(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="user_registration_otp")
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_code}"

    def key_expired(self):
        """Returns True if the OTP has expired."""
        return timezone.now() > self.expires_at


class Address(models.Model):
    """Consolidated Address Model for both ServiceProvider and Users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address')
    address = models.CharField(max_length=255, help_text="Service location address.")
    city = models.CharField(null=True, blank=True, max_length=100, help_text="City of the service location.")
    region = models.CharField(null=True, blank=True, max_length=100, help_text="Region of the service location.")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="user_addresses")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                   help_text="Latitude of the service location.")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                    help_text="Longitude of the service location.")
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.address)


class UserImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = ResizedImageField(
        upload_to='users/images/', size=[800, 800], quality=75, force_format='PNG',
        help_text='size of logo must be 800*800 and format must be png image file', crop=['middle', 'center']
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'User Image'
        verbose_name_plural = 'User Images'
        ordering = ['-created_at']


class UserContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = PhoneNumberField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Contact'
        verbose_name_plural = 'User Contacts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"


class BlockedUser(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blocked_users',
        help_text="The user who blocked another user."
    )
    blocked_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blocked_by',
        help_text="The user who is being blocked."
    )
    reason = models.TextField(blank=True, null=True, help_text="Optional reason for blocking the user.")

    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the user was blocked.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time when the block was last updated.")

    class Meta:
        unique_together = ['user', 'blocked_user']
        verbose_name = 'Blocked User'
        verbose_name_plural = 'Blocked Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} blocked {self.blocked_user.username}"


class ServiceProvider(models.Model):
    """Service Provider Profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider_profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20,
                              choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended')],
                              default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.company_name or 'Independent'}"

    @property
    def average_rating(self):
        return self.rating if self.total_reviews > 0 else "No reviews"

    def update_rating(self, new_rating):
        if not (0 <= new_rating <= 5):
            raise ValueError("Rating must be between 0 and 5.")
        total_score = self.rating * self.total_reviews
        self.total_reviews += 1
        self.rating = (total_score + new_rating) / self.total_reviews
        self.save()

    class Meta:
        verbose_name = "Service Provider"
        verbose_name_plural = "Service Providers"
        ordering = ['-created_at']

    def get_social_media(self):
        if hasattr(self, 'social_media'):
            return self.social_media
        return None

    def get_interests(self):
        if hasattr(self, 'interests'):
            return self.interests.all()
        return None

    def get_certifications(self):
        if hasattr(self, 'certifications'):
            return self.certifications.all()
        return None


class SocialMedia(models.Model):
    """Social Media Model for ServiceProvider"""
    service_provider = models.ForeignKey("ServiceProvider", related_name='social_media', on_delete=models.CASCADE)
    platform = models.CharField(max_length=100, verbose_name="Social Media Platform",
                                help_text="e.g., Facebook, Twitter, LinkedIn", null=True, blank=False)
    url = models.URLField(null=True, blank=False)

    def __str__(self):
        return f"Social Media for {self.service_provider.user.username}"


class Interest(models.Model):
    """Interests Model: Multiple Interests for Service Providers"""
    service_provider = models.ForeignKey("ServiceProvider", related_name='interests', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Interest Name")
    description = models.TextField(blank=True, null=True, verbose_name="Interest Description")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interest: {self.name}"


class Certification(models.Model):
    """Certification Model for Service Providers"""
    service_provider = models.ForeignKey("ServiceProvider", related_name='certifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Certification Name")
    certificate_file = models.FileField(upload_to='users/certifications/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Certification for {self.service_provider.user.username}"

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['-created_at']


class ServiceProviderLanguage(models.Model):
    """Language Model for User"""
    service_provider = models.ForeignKey("ServiceProvider", related_name='languages', on_delete=models.CASCADE)
    language = models.ForeignKey("core.Language", on_delete=models.CASCADE, related_name='service_providers')
    fluency = models.CharField(max_length=20, choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'),
                                                       ('advanced', 'Advanced')], default='advance')

    def __str__(self):
        return f"{self.language} - {self.fluency}"


class PasswordResetOTP(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="otp")
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if the OTP is still valid"""
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"OTP for {self.user.get_full_name} - {self.otp_code}"
