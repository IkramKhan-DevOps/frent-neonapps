from django.apps import apps
from django.contrib.auth import get_user_model
from payments.models import BasePayment
from django.db import models

""" HELPERS """


def get_connect_account_id(external_account_id):
    external_accounts = ExternalAccount.objects.filter(id=external_account_id)
    if external_accounts:
        return external_accounts[0].account_id
    return None


def get_user(connect_account_id):
    wallet = apps.get_model('finance', 'Wallet')

    wallets = wallet.objects.filter(stripe_account_id=connect_account_id)
    if wallets.exists():
        return wallets.first().user
    return None


""" MODELS """


class StripeCustomer(models.Model):
    STATUS_CHOICE = (
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),

        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
        ('incomplete_expired', 'Incomplete Expired'),

        ('trialing', 'Trialing'),
        ('paused', 'Paused'),
    )

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="stripe_customer")
    stripe_price = models.ForeignKey('Price', on_delete=models.SET_NULL, null=True, blank=True)
    customer_id = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255, null=True, blank=True)
    price_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    subscription_status = models.CharField(
        max_length=50, choices=STATUS_CHOICE, null=True, blank=True
    )
    subscription_full_response = models.JSONField(null=True, blank=True)

    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['created']
        verbose_name = 'Stripe Customer'
        verbose_name_plural = 'Stripe Customers'

    def __str__(self):
        return f'{self.user}'


class Product(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    image = models.URLField(help_text="Image URL", null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    default_price = models.CharField(
        max_length=255, help_text="The ID of the Price object that is the default price for this product.",
        null=True, blank=True
    )
    features = models.JSONField(null=True, blank=True)

    metadata = models.JSONField(null=True, blank=True)
    full_response = models.JSONField(null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField()

    class Meta:
        ordering = ['created']
        verbose_name = 'Stripe Package'
        verbose_name_plural = 'Stripe Packages'

    def __str__(self):
        return self.name

    def get_prices(self):
        return Price.objects.filter(product=self)


class Price(models.Model):
    TYPE_CHOICES = (
        ('recurring', 'Recurring'),
        ('one_time', 'One Time'),
    )
    USAGE_TYPE = (
        ('metered', 'Metered'),
        ('licensed', 'Licensed'),
    )
    INTERVAL_CHOICES = (
        ('month', 'Month'),
        ('year', 'Year'),
        ('week', 'Week'),
        ('day', 'Day'),
    )

    id = models.CharField(max_length=255, primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    currency = models.CharField(
        max_length=255, help_text="Three-letter ISO currency code"
    )
    unit_amount = models.IntegerField(
        help_text="The unit amount in cents to be charged, represented as a "
                  "whole integer if possible. Only set if billing_scheme=per_unit."
    )

    recurring = models.JSONField(null=True, blank=True)
    recurring_interval = models.CharField(
        max_length=100, default='month',
        choices=INTERVAL_CHOICES,
        help_text="he frequency at which a subscription is billed. One of day, week, month or year."
    )
    recurring_interval_count = models.IntegerField(default=1)
    recurring_usage_type = models.CharField(
        max_length=100, default='licensed', choices=USAGE_TYPE,
        help_text="One of metered or licensed."
    )

    metadata = models.JSONField(null=True, blank=True)
    full_response = models.JSONField(null=True, blank=True)

    type = models.CharField(max_length=50, default='recurring', choices=TYPE_CHOICES)
    active = models.BooleanField(default=True)
    created = models.DateTimeField()

    class Meta:
        ordering = ['created']
        verbose_name = 'Stripe Package Price'
        verbose_name_plural = 'Stripe Packages Prices'

    def __str__(self):
        return f"{self.product.name} - {self.unit_amount} {self.currency}"

    def get_real_price(self):
        return self.unit_amount / 100


class Transfer(models.Model):
    """
    available to input: amount*,  currency*, description, destination*, meta_data, source_type, transfer_group
    visit: https://stripe.com/docs/api/transfers/create
    alert: only required parameters are available locally.
    review: https://stripe.com/docs/connect/separate-charges-and-transfers#transfer-options
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    id = models.CharField(
        editable=False,
        max_length=255, primary_key=True, unique=True, help_text="Stripe Transfer ID"
    )
    amount = models.FloatField(
        help_text="A positive integer in cents representing how much to transfer."
    )
    currency = models.CharField(max_length=255, help_text="Three-letter ISO currency code")
    description = models.CharField(
        max_length=255, null=True,
        help_text="An arbitrary string attached to the object. Often useful for displaying to users."
    )
    destination = models.CharField(max_length=255)
    metadata = models.JSONField(
        null=True, blank=True,
        help_text="Set of key-value pairs that you can attach to an object. "
                  "This can be useful for storing additional information"
    )

    destination_payment = models.CharField(
        max_length=255,
        help_text="If the destination is a Stripe account, this will be the ID of the payment "
                  "that the destination account received for the transfer."
    )
    source_type = models.CharField(
        max_length=255, help_text="The source balance this transfer came from. One of card, fpx, or bank_account."
    )

    created = models.DateTimeField()
    full_response = models.JSONField(null=True, blank=True)

    class Meta:
        get_latest_by = "created"
        ordering = ["-created"]
        verbose_name_plural = "Transfers"

    def __str__(self):
        return f"Transfer {self.id}"


class Payout(models.Model):
    """
        available to input: amount*,  currency*, description, meta_data, statement_descriptor, source_type, transfer_group,
                            destination, method, source_type
        visit: https://stripe.com/docs/api/payouts/create
        alert: only required parameters are available locally.
    """

    PAYOUT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("canceled", "Canceled"),
        ("in_transit", "In Transit"),
    )
    PAYOUT_TYPE_CHOICES = (
        ("bank_account", "Bank Account"),
        ("card", "Card"),
    )

    id = models.CharField(max_length=255, primary_key=True, unique=True, help_text="Stripe Payout ID")
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField(help_text="A positive integer in cents representing how much to transfer.")

    currency = models.CharField(max_length=50, help_text="Three-letter ISO currency code")
    description = models.CharField(
        null=True, blank=True,
        max_length=1000, help_text="An arbitrary string attached to the object. Often useful for displaying to users."
    )

    destination = models.CharField(max_length=255, help_text="ID of the bank account or card the payout was sent to.")
    failure_balance_transaction = models.CharField(
        max_length=255, null=True, blank=True, help_text="ID of the balance transaction that failed."
    )
    failure_code = models.CharField(
        max_length=255, null=True, help_text="https://stripe.com/docs/api/payouts/failures"
    )
    failure_message = models.CharField(
        max_length=255, null=True,
        help_text="Message to user further explaining reason for payout failure if available."
    )
    metadata = models.JSONField()
    original_payout = models.CharField(max_length=255, null=True)
    source_type = models.CharField(
        max_length=255, help_text="The source balance this payout came from. One of card, fpx, or bank_account."
    )
    statement_descriptor = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Extra information about a payout to be displayed on the user’s bank statement."
    )

    arrival_date = models.DateTimeField(help_text="Date the payout is expected to arrive in the bank.")
    created = models.DateTimeField(help_text="Date the payout was created.")

    # Current status of the payout: paid, pending, in_transit, canceled or failed.
    # A payout is pending until it is submitted to the bank, when it becomes in_transit.
    # The status then changes to paid if the transaction goes through,
    # or to failed or canceled (within 5 business days).
    # Some failed payouts may initially show as paid but then change to failed.
    status = models.CharField(max_length=50, default="pending", choices=PAYOUT_STATUS_CHOICES)
    type = models.CharField(
        max_length=50, default="bank_account", choices=PAYOUT_TYPE_CHOICES,
        help_text="The type of the payout: 'bank_account' or 'card'"
    )

    full_response = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Payout {self.id}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        connect_id = get_connect_account_id(self.destination)
        if connect_id:
            user = get_user(connect_id)
            if user:
                self.user = user

        return super().save(force_insert, force_update, using, update_fields)


class ExternalAccount(models.Model):
    OBJECT_TYPE = (
        ("card", "Card"),
        ("bank_account", "Bank Account"),
    )

    id = models.CharField(max_length=255, primary_key=True, unique=True, help_text="Stripe Payout ID")
    account_id = models.CharField(max_length=255, unique=False)

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=False, editable=False)
    object = models.CharField(max_length=50, choices=OBJECT_TYPE, default="bank_account")
    country = models.CharField(max_length=255, null=True, blank=True)
    fingerprint = models.CharField(max_length=255, null=True, blank=True)
    full_response = models.JSONField(null=True, blank=True)
    last4 = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    bank_status = models.CharField(max_length=255, null=True, blank=True)
    bank_account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account_holder_type = models.CharField(max_length=255, null=True, blank=True)
    bank_bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_routing_number = models.CharField(max_length=255, null=True, blank=True)
    bank_currency = models.CharField(max_length=255, null=True, blank=True)

    card_address_city = models.CharField(max_length=255, null=True, blank=True)
    card_address_country = models.CharField(max_length=255, null=True, blank=True)
    card_address_line1 = models.CharField(max_length=255, null=True, blank=True)
    card_address_line1_check = models.CharField(max_length=255, null=True, blank=True)
    card_address_line2 = models.CharField(max_length=255, null=True, blank=True)
    card_address_state = models.CharField(max_length=255, null=True, blank=True)
    card_address_zip = models.CharField(max_length=255, null=True, blank=True)
    card_address_zip_check = models.CharField(max_length=255, null=True, blank=True)
    card_brand = models.CharField(max_length=255, null=True, blank=True)
    card_cvc_check = models.CharField(max_length=255, null=True, blank=True)
    card_last4 = models.CharField(max_length=255, null=True, blank=True)
    card_exp_month = models.SmallIntegerField(null=True, blank=True)
    card_exp_year = models.SmallIntegerField(null=True, blank=True)
    card_funding = models.CharField(max_length=255, null=True, blank=True)
    card_name = models.CharField(max_length=255, null=True, blank=True)
    card_tokenization_method = models.CharField(max_length=255, null=True, blank=True)
    card_wallet = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Bank Account: {self.id}'

    def is_card(self):
        return self.object == 'card'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        user = get_user(self.account_id)
        if user:
            self.user = user
        return super().save(force_insert, force_update, using, update_fields)
