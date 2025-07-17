import random
import re
from allauth.account.models import EmailConfirmation, EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer, VerifyEmailSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers
from twilio.rest import Client

from root import settings
from src.services.users.models import User, PasswordResetOTP, UserRegistrationOTP
from django.utils.translation import gettext_lazy as _


class ValidationMixin:
    """Mixin to provide reusable email and phone number validation."""

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    phone_regex = r'^\+?[0-9]{10,15}$'

    def is_valid_email(self, email):
        """Validate email format."""
        return re.match(self.email_regex, email) is not None

    def is_valid_phone(self, phone):
        """Validate phone number format."""
        return re.match(self.phone_regex, phone) is not None


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'first_name', 'last_name']
        read_only_fields = ['pk', 'email']


class CustomLoginSerializer(serializers.Serializer, ValidationMixin):
    """Custom serializer for login with email or phone number."""

    phone_number = serializers.CharField(label='Phone Number', max_length=50)
    password = serializers.CharField(label='Password', write_only=True)

    def validate_phone_number(self, value):
        """Validate email or phone number field."""
        if not self.is_valid_phone(value):
            raise serializers.ValidationError("Phone Number is not valid.")
        return value

    def validate(self, attrs):
        """Validate login credentials."""
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        # Check if the input is an email or phone number
        user = User.objects.filter(
            models.Q(phone_number=phone_number) | models.Q(phone_number=phone_number)
        ).first()

        if user is None:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        if not user.user_registration_completed():
            raise serializers.ValidationError("User is not verified Yet")

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        attrs['user'] = user
        return attrs


class CustomRegisterSerializer(serializers.Serializer):
    """Custom serializer for user registration with username, phone number, and password."""

    username = serializers.CharField(max_length=150, required=True)
    phone_number = serializers.CharField(max_length=15, required=True)
    password1 = serializers.CharField(write_only=True, min_length=8, required=True)
    password2 = serializers.CharField(write_only=True, min_length=8, required=True)

    def validate_username(self, value):
        """Ensure username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_phone_number(self, value):
        """Validate unique phone number and phone number format."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        if not re.match(r'^\+\d{10,15}$', value):
            raise serializers.ValidationError(
                "Phone number must start with '+' followed by 10 to 15 digits (including country code)."
            )
        return value

    def validate(self, data):
        """Ensure passwords match."""
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return data

    def send_sms(self, to_number, verification_key):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your verification code is: {verification_key}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(to_number)
        )
        return message.sid

    def create(self, validated_data):
        """Create the user using Django's password hashing mechanism."""
        username = validated_data['username']
        phone_number = validated_data['phone_number']
        password = validated_data['password1']

        user = User(username=username, phone_number=phone_number)
        user.set_password(password)
        user.save()

        # Generate and save OTP
        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        UserRegistrationOTP.objects.create(user=user, otp_code=otp, expires_at=expires_at)

        # Send OTP via SMS
        self.send_sms(phone_number, otp)

        return user


class ResendVerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)

    def validate_phone_number(self, value):
        """Validate if the phone number exists and OTP is not already verified."""
        try:
            user = User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this phone number.")

        try:
            otp = user.user_registration_otp
            if otp.is_verified:
                raise serializers.ValidationError("This phone number is already verified.")
        except UserRegistrationOTP.DoesNotExist:
            pass  # If no OTP exists, allow creation

        return value

    def send_sms(self, to_number, verification_key):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your verification code is: {verification_key}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(to_number)
        )
        return message.sid

    def save(self):
        phone_number = self.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)

        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=10)

        UserRegistrationOTP.objects.update_or_create(
            user=user,
            defaults={'otp_code': otp, 'expires_at': expires_at}
        )

        self.send_sms(user.phone_number, otp)
        return {"detail": "A new verification code has been sent to your phone number."}


class VerificationConfirmationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)
    otp = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp = attrs.get('otp')

        try:
            phone_number_confirmation = UserRegistrationOTP.objects.get(
                user__phone_number=phone_number, otp_code=otp
            )
        except UserRegistrationOTP.DoesNotExist:
            raise serializers.ValidationError(_("Invalid phone number or OTP."))

        if phone_number_confirmation.key_expired():
            raise serializers.ValidationError(_("The OTP has expired."))

        if phone_number_confirmation.is_verified:
            raise serializers.ValidationError(_("The User is already Registered."))
        self.phone_number_confirmation = phone_number_confirmation
        return attrs

    def confirm_verification(self):
        self.phone_number_confirmation.is_verified = True
        self.phone_number_confirmation.save()
        return self.phone_number_confirmation.user  # optional: return user object


class PasswordSerializer(serializers.Serializer):
    """Serializer for password input."""

    password = serializers.CharField(required=True, write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)

    def validate_phone_number(self, value):
        """Check if email exists in the database"""
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("No user found with this phone number.")
        return value

    def send_sms(self, to_number, verification_key):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your verification code is: {verification_key}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(to_number)  # Convert to string here
        )
        return message.sid

    def save(self):
        """Generate OTP and send it to the user"""
        phone_number = self.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        PasswordResetOTP.objects.filter(user=user).delete()
        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        PasswordResetOTP.objects.create(user=user, otp_code=otp, expires_at=expires_at)
        self.send_sms(user.phone_number, otp)


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate OTP and passwords"""
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone_number": "Invalid phone number."})
        try:
            otp_obj = PasswordResetOTP.objects.get(user=user, otp_code=otp)
            if otp_obj.expires_at < timezone.now():
                raise serializers.ValidationError({"otp": "OTP has expired."})
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        data['user'] = user
        return data

    def save(self):
        """Reset the user's password"""
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        PasswordResetOTP.objects.filter(user=user).delete()
