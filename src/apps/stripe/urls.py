from django.urls import path, include
from .views import (
    ConnectWalletCreateView, ConnectWalletVisitView, ConnectWalletView, StripeWebHook, StripeRefreshTemplateView,
    StripeReturnTemplateView,
)

app_name = 'stripe'
# VENDOR END POINTS
urlpatterns = [

    path('connect-wallet/', ConnectWalletView.as_view(), name='connect-wallet'),
    path('connect-wallet/create/', ConnectWalletCreateView.as_view(), name='connect-wallet-create'),
    path('connect-wallet/visit/', ConnectWalletVisitView.as_view(), name='connect-wallet-visit'),
    path('connect-wallet/refresh/', StripeRefreshTemplateView.as_view(), name='connect-wallet-refresh'),
    path('connect-wallet/return/', StripeReturnTemplateView.as_view(), name='connect-wallet-return'),

]

urlpatterns += [
    path('stripe/api/', include('src.apps.stripe.api.urls', namespace='stripe-api')),
]

# WEBHOOK END POINT
urlpatterns += [
    path('hook/', StripeWebHook.as_view(), name='stripe-webhook'),
]
