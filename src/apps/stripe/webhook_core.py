import stripe
from django.http import HttpResponse

STRIPE_WEBHOOK_SECRET = "whsec_r513JxZOoONEN5nedblCPT5SePqLcjWG"
from src.apps.stripe.webhooks_bll import (
    webhook_account_updated, webhook_transfer_updated, webhook_subscription_created,
    webhook_subscription_deleted, webhook_subscription_updated, webhook_payout_created, webhook_payout_status_change,
    webhook_payout_updated, webhook_external_account_updated, webhook_account_external_account_deleted,
    webhook_external_account_created
)

""" HOOKS LOGIC ---------------------------------------------------------------------------------------------------- """


class WebhookControl:

    def __init__(self, event, event_type, data):
        self.event = event
        self.event_type = event_type
        self.data = data

    def command_control(self):
        command = self.event_type.split('.')[0]
        sub_command = self.event_type.split('.')[1] or None

        if command == 'account':
            self.hooks_accounts() if sub_command != "external_account" else self.hooks_external_accounts()

        elif command == 'transfer':
            self.hooks_transfers()

        elif command == 'payout':
            self.hooks_payouts()

        elif command == 'topup':
            self.hooks_top_up()

        elif command == 'customer':
            self.hooks_customer() if sub_command != "subscription" else self.hooks_subscription()

        elif command == 'subscription_schedule':
            self.hooks_subscription_schedule()

        elif command == 'checkout':
            self.hooks_checkout()

        elif command == 'refund':
            self.hooks_refund()

    def hooks_accounts(self):
        if self.event_type == 'account.updated':
            print(f"HOOK -> {self.event_type}")
            webhook_account_updated(self.event, self.data)

    def hooks_external_accounts(self):
        if self.event_type == 'account.external_account.created':
            print(f"HOOK -> {self.event_type}")
            webhook_external_account_created(self.event, self.data)

        elif self.event_type == 'account.external_account.deleted':
            print(f"HOOK -> {self.event_type}")
            webhook_account_external_account_deleted(self.event, self.data)

        elif self.event_type == 'account.external_account.updated':
            print(f"HOOK -> {self.event_type}")
            webhook_external_account_updated(self.event, self.data)

    def hooks_transfers(self):
        if self.event_type == 'transfer.created':
            print(f"HOOK -> {self.event_type}")
            webhook_transfer_updated(self.event, self.data)

        elif self.event_type == 'transfer.reversed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'transfer.updated':
            print(f"HOOK -> {self.event_type}")
            webhook_transfer_updated(self.event, self.data)

    def hooks_payouts(self):
        if self.event_type == 'payout.canceled':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'payout.created':
            print(f"HOOK -> {self.event_type}")
            webhook_payout_created(self.event, self.data)

        elif self.event_type == 'payout.failed':
            print(f"HOOK -> {self.event_type}")
            webhook_payout_status_change(self.event, self.data, "failed")

        elif self.event_type == 'payout.paid':
            print(f"HOOK -> {self.event_type}")
            webhook_payout_status_change(self.event, self.data, "paid")

        elif self.event_type == 'payout.reconciliation_completed':
            print(f"HOOK -> {self.event_type}")
            webhook_payout_status_change(self.event, self.data, "reconciliation_completed")

        elif self.event_type == 'payout.updated':
            print(f"HOOK -> {self.event_type}")
            webhook_payout_updated(self.event, self.data)

    def hooks_top_up(self):
        if self.event_type == 'topup.canceled':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'topup.created':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'topup.failed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'topup.reversed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'topup.succeeded':
            print(f"HOOK -> {self.event_type}")

    def hooks_customer(self):
        if self.event_type == 'customer.created':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'customer.deleted':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'customer.updated':
            print(f"HOOK -> {self.event_type}")

    def hooks_subscription(self):
        if self.event_type == 'customer.subscription.created':
            print(f"HOOK -> {self.event_type}")
            webhook_subscription_created(self.event, self.data)

        elif self.event_type == 'customer.subscription.updated':
            print(f"HOOK -> {self.event_type}")
            webhook_subscription_updated(self.event, self.data)

        elif self.event_type == 'customer.subscription.deleted':
            print(f"HOOK -> {self.event_type}")
            webhook_subscription_deleted(self.event, self.data)

        elif self.event_type == 'customer.subscription.paused':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'customer.subscription.pending_update_applied':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'customer.subscription.pending_update_expired':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'customer.subscription.resumed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'customer.subscription.trial_will_end':
            print(f"HOOK -> {self.event_type}")

    def hooks_subscription_schedule(self):
        if self.event_type == 'subscription_schedule.aborted':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'subscription_schedule.canceled':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'subscription_schedule.completed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'subscription_schedule.created':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'subscription_schedule.expiring':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'subscription_schedule.released':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'subscription_schedule.updated':
            print(f"HOOK -> {self.event_type}")

    def hooks_checkout(self):
        if self.event_type == 'checkout.session.async_payment_failed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'checkout.session.async_payment_succeeded':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'checkout.session.completed':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'checkout.session.expired':
            print(f"HOOK -> {self.event_type}")

    def hooks_refund(self):
        if self.event_type == 'refund.created':
            print(f"HOOK -> {self.event_type}")

        elif self.event_type == 'refund.updated':
            print(f"HOOK -> {self.event_type}")


""" HOOKS  -------------------------------------------------------------------------------------------------------- """


def hooks_view(request):
    print("WEBHOOK HIT")
    webhook_secret = STRIPE_WEBHOOK_SECRET
    signature = request.META['HTTP_STRIPE_SIGNATURE']
    payload = request.body
    print("STRIPE_WEBHOOK_SECRET", STRIPE_WEBHOOK_SECRET)
    print("HTTP_STRIPE_SIGNATURE", signature)
    print("payload", payload)

    try:

        event = stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=webhook_secret)
        print("event", event)
        webhook_control = WebhookControl(event, event['type'], event['data'])
        print("event", webhook_control)
        webhook_control.command_control()
        return HttpResponse(status=200)

    except ValueError as e:
        error = e
    except stripe.error.SignatureVerificationError as e:
        error = e
    except Exception as e:
        error = e

    print(error)
    return HttpResponse(status=400)
