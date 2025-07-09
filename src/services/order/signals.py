from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.services.order.models import Order


@receiver(post_save, sender=Order)
def handle_order_payment(sender, instance, created, **kwargs):
    """Handles the wallet balance when order is created and Payment is completed."""
    if instance.order_status == 'pending' and instance.payment_status == 'completed':
        wallet = apps.get_model('finance', 'Wallet')
        provider_wallet = wallet.objects.get(user=instance.service_request.service.provider)
        provider_wallet.balance_pending += instance.paid_price
        provider_wallet.save()


@receiver(post_save, sender=Order)
def transfer_pending_to_balance(sender, instance, created, **kwargs):
    """Transfers the pending balance to available balance once the order is completed."""
    if instance.order_status == 'completed' and instance.payment_status == 'completed':
        wallet = apps.get_model('finance', 'Wallet')
        provider_wallet = wallet.objects.get(user=instance.service_request.service.provider)
        if provider_wallet.balance_pending > 0:
            provider_wallet.balance_available += provider_wallet.balance_pending
            provider_wallet.balance_pending = 0
            provider_wallet.save()

