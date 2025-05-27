from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, ServiceProvider


@receiver(post_save, sender=User, dispatch_uid="create_service_provider_profile")
def create_service_provider_profile(sender, instance, created, **kwargs):
    """
    Signal to create a ServiceProvider profile for the user
    if the user type is 'service_provider'.
    """
    service_provider_exists = hasattr(instance, 'service_provider_profile')
    service_provider = apps.get_model('users', 'ServiceProvider')
    if not service_provider_exists:
        service_provider.objects.get_or_create(user=instance)


@receiver(post_save, sender=User, dispatch_uid="create_user_address")
def create_user_address(sender, instance, created, **kwargs):
    """
    Signal to create an Address for the user
    if the user does not already have one.
    """
    address_exists = hasattr(instance, 'address')
    address = apps.get_model('users', 'Address')
    if not address_exists:
        address.objects.get_or_create(user=instance)


@receiver(post_save, sender=User, dispatch_uid="create_user_wallet")
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal to create a Wallet for the user
    if the user does not already have one.
    """
    wallet_exists = hasattr(instance, 'user_wallet')
    wallet = apps.get_model('finance', 'Wallet')
    if not wallet_exists:
        wallet.objects.get_or_create(user=instance)
