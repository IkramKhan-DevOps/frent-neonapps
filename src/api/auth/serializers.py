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
from src.services.users.models import User, PasswordResetOTP
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

    email = serializers.CharField(label='Email/Phone Number', max_length=50)
    password = serializers.CharField(label='Password', write_only=True)

    def validate_email(self, value):
        """Validate email or phone number field."""
        if not self.is_valid_email(value) and not self.is_valid_phone(value):
            raise serializers.ValidationError("Email or Phone Number is not valid.")
        return value

    def validate(self, attrs):
        """Validate login credentials."""
        email = attrs.get('email')
        password = attrs.get('password')

        # Check if the input is an email or phone number
        user = User.objects.filter(
            models.Q(email=email) | models.Q(phone_number=email)
        ).first()

        if user is None:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        # Check Email Verification
        email_address = EmailAddress.objects.filter(
            user=user, email=email).first()
        if email_address and not email_address.verified:
            raise serializers.ValidationError("User is not verified.")

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        attrs['user'] = user
        return attrs


class CustomRegisterSerializer(RegisterSerializer):
    """Custom serializer for user registration."""

    phone_number = serializers.CharField(max_length=15, required=True)

    def validate_email(self, email):
        """Validate unique email."""
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate_phone_number(self, value):
        print("Validating phone number:", value)  # or use logging

        """Validate unique phone number and phone number format."""
        # Check for uniqueness
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")

        # Validate phone number format (only digits, 10-15 characters)
        if not re.match(r'^\+\d{10,15}$', value):
            raise serializers.ValidationError(
                "Phone number must start with '+' followed by 10 to 15 digits (including country code)."
            )
        return value

    def save(self, request):
        user = super().save(request)
        user.phone_number = self.validated_data.get('phone_number')
        user.save()
        return user


class PasswordSerializer(serializers.Serializer):
    """Serializer for password input."""

    password = serializers.CharField(required=True, write_only=True)


class EmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        # Validate EmailConfirmation existence
        try:
            email_confirmation = EmailConfirmation.objects.get(
                email_address__email=email, key=otp
            )
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError(_("Invalid email or OTP."))

        # Check if the OTP has expired
        if email_confirmation.key_expired():
            raise serializers.ValidationError(_("The OTP has expired."))

        attrs['email_confirmation'] = email_confirmation
        return attrs

    def confirm_email(self):
        email_confirmation = self.validated_data['email_confirmation']
        email_address = email_confirmation.confirm(self.context.get('request'))
        return email_address


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if email exists in the database"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

    def send_otp_email(self, email, otp):
        context = {
            "otp": otp
        }
        template_name = "account/password_reset_otp.html"
        convert_to_html_content = render_to_string(
            template_name=template_name,
            context=context
        )
        plain_message = strip_tags(convert_to_html_content)
        send_mail(
            subject="Password Reset OTP",
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email, ],
            html_message=convert_to_html_content,
            fail_silently=True
        )

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
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        PasswordResetOTP.objects.filter(user=user).delete()
        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        PasswordResetOTP.objects.create(user=user, otp_code=otp, expires_at=expires_at)
        self.send_otp_email(email, otp)
        if user.phone_number:
            try:
                self.send_sms(user.phone_number, otp)
            except Exception as e:
                raise serializers.ValidationError({"sms": "Failed to send OTP via SMS."})


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate OTP and passwords"""
        email = data.get('email')
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
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Invalid email."})
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
