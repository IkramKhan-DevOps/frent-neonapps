import random

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from django.shortcuts import resolve_url
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from twilio.rest import Client

from root import settings


class MyAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        return resolve_url('account_set_password')

    def get_login_redirect_url(self, request):
        # Check if the user has a usable password
        user = request.user
        if user.is_authenticated and user.has_usable_password():
            return resolve_url('/')

        else:
            return resolve_url('account_set_password')

    def respond_user_authenticated(self, request, user):
        """
        Called when a user is authenticated successfully.
        """
        # Redirect based on whether the user has a usable password
        if user.has_usable_password():
            return HttpResponseRedirect(reverse('account_set_password'))
        else:
            return HttpResponseRedirect(reverse('/'))

    def send_sms(self, to_number, verification_key):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your verification code is: {verification_key}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(to_number)  # Convert to string here
        )
        return message.sid

    def send_confirmation_mail(self, request, emailconfirmation, signup):

        # Generate the verification key
        verification_key = str(random.randint(100000, 999999))
        # Get or create EmailConfirmation
        emailconfirmation, created = EmailConfirmation.objects.get_or_create(
            email_address=emailconfirmation.email_address,
            key=verification_key
        )
        print("Email Confirmation:", emailconfirmation)
        emailconfirmation.sent = timezone.now()
        emailconfirmation.save()

        # Prepare the email context
        context = {
            "user": emailconfirmation.email_address.user,
            "key": verification_key,
        }

        # Send the custom email with the verification key
        self.send_mail("account/email/email_verification_key", emailconfirmation.email_address.email, context)

        user = emailconfirmation.email_address.user
        # Send the verification key via SMS
        if hasattr(user, 'phone_number') and user.phone_number:
            try:
                self.send_sms(user.phone_number, verification_key)
            except Exception as e:
                print(f"Failed to send SMS: {e}")

    def get_email_confirmation_url(self, request, emailconfirmation):
        return emailconfirmation.key
