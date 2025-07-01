from datetime import datetime
import pytz
import stripe
from root.bll import convert_cents_to_decimal
from root.settings import STRIPE_SECRET_KEY
from src.apps.stripe.dll import ExternalAccountDLL, BalanceDLL
from src.apps.stripe.helpers import get_full_url, get_date_time
from src.apps.stripe.models import Transfer, Product, Price, StripeCustomer

from django.utils import timezone

from src.apps.stripe.notifier import notify_transfer_created

stripe.api_key = "sk_test_51LC794Js59MkLRK8jKm97MecFP4dwcOrxfetIXefvByCaodNGQ1qNdKqaxVBZGD1aW9VTBh69W73T1Ox7LtByRpy00nRXonBff"

""" STRIPE CONNECT ------------------------------------------------------------------------------------------------- """
""" CONNECT API CALLS """


# TESTED - REQUIRED - CONNECT
def stripe_connect_account_create(user):
    error = ""
    account = None

    if not user.get_address().country:
        return "User doesn't have any country selected", None

    try:
        account = stripe.Account.create(
            type='express', country=user.get_address().country.short_name, email=user.email,
        )
        wallet = user.get_user_wallet()
        wallet.stripe_account_id = account.id
        wallet.stripe_description = account
        wallet.stripe_account_country = user.get_address().country.short_name
        wallet.stripe_account_email = user.email
        wallet.stripe_account_type = "express"
        wallet.save()

    except stripe.error.StripeError as e:
        error = e
    except Exception as e:
        error = e

    return error, account


# TESTED - REQUIRED - CONNECT
def stripe_connect_account_link(connect_account_id):
    error = ""
    url = None

    try:

        refresh_url = get_full_url('website:home')
        return_url = get_full_url('website:home')

        account_link = stripe.AccountLink.create(
            account=connect_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        url = account_link['url']

    except stripe.error.StripeError as e:
        error = e
    except Exception as e:
        error = e

    return error, url


# TESTED - REQUIRED - CONNECT
def get_connect_wallet_balance(user):
    user_wallet = user.get_user_wallet()
    connect_account_id = user_wallet.stripe_account_id

    if not connect_account_id:
        return "User doesn't have any connect account", None

    if not user.is_stripe_account_active():
        return "User doesn't have a verified connect account", None

    error = ""
    balance = None

    try:
        balance = stripe.Balance.retrieve(stripe_account=connect_account_id)
        available_balance = convert_cents_to_decimal(balance['available'][0]['amount'])
        available_balance_currency = balance['available'][0]['currency']
        pending_balance = convert_cents_to_decimal(balance['pending'][0]['amount'])
        pending_balance_currency = balance['pending'][0]['currency']

        balance_data = BalanceDLL(
            available_balance=available_balance,
            available_balance_currency=available_balance_currency,
            pending_balance=pending_balance,
            pending_balance_currency=pending_balance_currency
        )

        user_wallet.connect_available_balance = balance_data.available_balance
        user_wallet.connect_pending_balance = balance_data.pending_balance
        user_wallet.connect_available_balance_currency = balance_data.available_balance_currency
        user_wallet.connect_pending_balance_currency = balance_data.pending_balance_currency
        user_wallet.save()

        return error, balance_data
    except stripe.error.StripeError as e:
        # Handle error
        error = e
    except Exception as e:
        error = e

    return error, balance


# TESTED - REQUIRED - CONNECT
def stripe_payout_to_connect_account(user, amount, destination_id=None):
    """need verification"""
    error = ""
    payout = None

    user_wallet = user.get_user_wallet()
    connect_account_id = user_wallet.stripe_account_id

    if not user.is_stripe_account_active():
        return "User doesn't have a verified connect account", None

    try:
        payout = stripe.Payout.create(
            amount=amount * 100,
            currency="eur",
            stripe_account=connect_account_id,
        )
    except stripe.error.StripeError as e:
        error = e
    except Exception as e:
        error = e

    return error, payout


# TESTED - REQUIRED - CONNECT
def stripe_transfer_to_connect_account(user, amount):
    """need verification"""
    success = False
    message = ""
    obj = None

    user_wallet = user.get_user_wallet()
    connect_account_id = user_wallet.stripe_account_id
    amount = int(amount)

    if not amount:
        return False, "Amount is required"

    if amount > user.get_available_balance():
        return False, "Insufficient balance"

    if not user.is_stripe_account_active():
        return False, "User doesn't have a verified connect account"

    try:
        transfer = stripe.Transfer.create(
            amount=amount * 100,
            currency="eur",
            destination=connect_account_id,
        )

        obj = Transfer.objects.create(
            id=transfer.get('id'),
            user=user,
            amount=amount,
            currency=transfer.get('currency'),
            description=transfer.get('description'),
            destination=transfer.get('destination'),
            destination_payment=transfer.get('destination_payment'),
            source_type=transfer.get('source_type'),
            metadata=transfer.get('metadata'),
            created=timezone.now(),
            full_response=transfer,
        )
        success = True

        # NOTIFY
        notify_transfer_created(obj)
        return success, obj

    except stripe.error.StripeError as e:
        message = e
    except Exception as e:
        message = e

    return success, message


# TODO: REMOVE > this function later (not required)
def get_external_accounts_from_stripe(user):
    """completed"""

    stripe_connect_account_id = user.get_user_wallet().stripe_account_id
    if not stripe_connect_account_id:
        return None

    response = stripe.Account.list_external_accounts(account=stripe_connect_account_id)
    external_accounts = []

    data = response.get('data', [])

    for account_data in data:
        external_account = ExternalAccountDLL(account_data)
        external_accounts.append(external_account)

    return external_accounts


""" SUBSCRIPTION BLL ----------------------------------------------------------------------------------------------- """
""" PACKAGES - PRODUCTS - PRICES ETC """


# TESTED - REQUIRED - DATA
def get_price_list():
    try:
        prices = stripe.Price.list()
        price_list = []

        for price in prices:
            price_list.append(price)

        return True, price_list
    except stripe.error.StripeError as e:
        message = e
    except Exception as e:
        message = e

    return False, message


# TESTED - REQUIRED - DATA
def get_plan_list():
    plans = stripe.Plan.list()
    plan_list = []

    for plan in plans:
        plan_list.append(plan)

    return plan_list


# TESTED - REQUIRED - DATA
def get_product_list():
    message = ""

    try:

        products = stripe.Product.list()
        product_list = []

        for product in products:
            product_list.append(product)

        return True, product_list

    except stripe.error.StripeError as e:
        message = e
    except Exception as e:
        message = e

    return False, message


# TESTED - REQUIRED - DATA
def update_product_list():
    success, obj = get_product_list()

    if success:
        for product in obj:
            product_id = product.get('id')
            product_name = product.get('name')
            product_image = product.get('images')[0] if product.get('images') else None
            product_description = product.get('description')
            product_default_price = product.get('default_price')
            product_metadata = product.get('metadata')

            timestamp = product.get('created')
            naive_datetime = datetime.fromtimestamp(timestamp)
            timezone = pytz.UTC
            product_created = naive_datetime.replace(tzinfo=timezone)

            if not Product.objects.filter(id=product_id):
                product_obj = Product.objects.create(
                    id=product_id,
                    name=product_name,
                    image=product_image,
                    description=product_description,
                    default_price=product_default_price,
                    metadata=product_metadata,
                    active=True,
                    created=product_created,
                    full_response=product
                )
                product_obj.save()
                print("Product saved with ID: ", product_id)
            else:
                print("Product already exists with ID: " + product_id)
        return True, "Products updated Successfully"

    return False, obj


# TESTED - REQUIRED - DATA
def update_price_list():
    # FIRST UPDATE PRODUCTS
    success_product, obj_product = update_product_list()
    if not success_product:
        return False, obj_product

    # UPDATE PRICE NOW
    success, obj = get_price_list()

    if success:
        for price in obj:
            recurring = price.get('recurring')
            price_recurring = recurring
            price_recurring_interval = recurring.get('interval')
            price_recurring_interval_count = recurring.get('interval_count')
            price_interval_usage_type = recurring.get('usage_type')

            price_id = price.get('id')
            price_unit_amount = price.get('unit_amount') or 0
            price_currency = price.get('currency')
            price_product = price.get('product')
            price_metadata = price.get('metadata')
            price_full_response = price.get('full_response')
            price_type = price.get('type')
            price_active = price.get('active')

            timestamp = price.get('created')
            naive_datetime = datetime.fromtimestamp(timestamp)
            timezone = pytz.UTC
            price_created = naive_datetime.replace(tzinfo=timezone)

            if not Price.objects.filter(id=price_id):
                product = Product.objects.filter(id=price_product)

                if product:
                    price_obj = Price.objects.create(
                        id=price_id,
                        unit_amount=price_unit_amount,
                        currency=price_currency,
                        product=product[0],
                        metadata=price_metadata,
                        active=price_active,
                        recurring=price_recurring,
                        recurring_interval=price_recurring_interval,
                        recurring_interval_count=price_recurring_interval_count,
                        recurring_usage_type=price_interval_usage_type,
                        created=price_created,
                        type=price_type,
                        full_response=price,

                    )
                    print("Price saved with ID: ", price_id)
                else:
                    print("Product doesn't exists in local database - i am calling Spider man to add Products")
                    update_product_list()
                    update_price_list()
            else:
                print("Price already exists with ID: " + price_id)
        return True, "Prices updated Successfully"

    return False, obj


""" SUBSCRIPTION API CALLS """


# TESTED - REQUIRED - DATA
def stripe_subscription_retrieve(id):
    try:
        subscription = stripe.Subscription.retrieve(id)
        return True, subscription
    except stripe.error.StripeError as e:
        message = e
    except Exception as e:
        message = e

    return False, message


""" SUBSCRIPTION LOCAL FUNCTIONS"""


# TESTED - REQUIRED - DATA
def update_subscription_record(id):
    success, obj = stripe_subscription_retrieve(id)
    customer = StripeCustomer.objects.filter(subscription_id=id)
    if success and customer:
        price_id = obj.get('items').get('data')[0].get('price').get('id')
        prices = Price.objects.filter(id=price_id)
        customer = customer[0]
        customer.subscription_id = obj.get('id')
        customer.subscription_status = obj.get('status')
        customer.subscription_end = get_date_time(obj.get('current_period_end'))
        customer.subscription_start = get_date_time(obj.get('current_period_start'))
        customer.created = get_date_time(obj.get('created'))
        customer.price_id = price_id
        customer.stripe_price = prices[0]
        customer.subscription_full_response = obj
        customer.save()

        return True, customer
    return False, None


""" CUSTOMER BLL --------------------------------------------------------------------------------------------------- """
""" CUSTOMER API CALLS """


# TODO: LATER
def stripe_customer_create(user):
    """completed"""
    try:

        customer = stripe.Customer.create(

            email=user.email,
            name=user,
            description=user.get_full_name(),
            metadata={
                'user_username': user.username,
                'user_id': user.id,
            }
        )

        return True, customer
    except stripe.error.StripeError as e:
        message = e
    except Exception as e:
        message = e

    return False, message
