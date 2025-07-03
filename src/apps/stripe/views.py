from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from src.apps.stripe.bll import (
    stripe_connect_account_create, stripe_connect_account_link,
)
from .webhook_core import hooks_view

""" VENDOR VIEWS FOR STRIPE -------------------------------------------------------------------------------------- """


@method_decorator(login_required, name='dispatch')
class ConnectWalletView(View):

    def get(self, request, *args, **kwargs):
        if not request.user.country:
            messages.error(request, 'You have not provided your country, kindly update your first')
            return redirect("vendor:account_change")

        return render(request, 'stripe/connect_wallet.html')


@method_decorator(login_required, name='dispatch')
class ConnectWalletCreateView(View):

    def get(self, request, *args, **kwargs):
        user = request.user

        # Show warning message if user already connected wallet
        if user.is_stripe_connected():
            messages.warning(request, 'You have already connected your wallet')
            return redirect(request.META.get('HTTP_REFERER'))

        error, account = stripe_connect_account_create(user)

        # Show error message if error occurred
        if error:
            messages.error(request, error)
            return redirect(request.META.get('HTTP_REFERER'))

        # Successfully connected wallet
        messages.success(request, 'Your wallet has been connected successfully')
        return redirect(request.META.get('HTTP_REFERER'))


@method_decorator(login_required, name='dispatch')
class ConnectWalletVisitView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        wallet = user.get_user_wallet()

        # Show warning message if user ie not connected
        if not user.is_stripe_connected():
            messages.warning(request, 'You have not connected your wallet')
            return redirect(request.META.get('HTTP_REFERER'))

        error, url = stripe_connect_account_link(wallet.stripe_account_id)

        # Show error message if error occurred
        if error:
            messages.error(request, error)
            return redirect(request.META.get('HTTP_REFERER'))

        # Successfully connected wallet
        return redirect(url)


# class ConnectWalletConnected()


class StripeRefreshTemplateView(TemplateView):
    template_name = 'stripe/refresh.html'


class StripeReturnTemplateView(TemplateView):
    template_name = 'stripe/success.html'


""" WEBHOOK VIEWS FOR STRIPE -------------------------------------------------------------------------------------- """


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebHook(View):

    def post(self, request, *args, **kwargs):
        return hooks_view(request)
