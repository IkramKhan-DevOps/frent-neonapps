from django.urls import path

from src.apps.stripe.api.views import ConnectWalletCreateAPIView, ConnectWalletActivateAPIView, PayoutListAPIView, \
    TransferListAPIView, ConnectWalletRefreshView, ConnectWalletVisitAPIView

app_name = 'stripe-api'
urlpatterns = [
    path('connect-wallet/', ConnectWalletCreateAPIView.as_view(), name='connect_wallet'),
    path('wallet-visit/', ConnectWalletVisitAPIView.as_view(), name='wallet-visit'),

    path('connect-wallet/activate/', ConnectWalletActivateAPIView.as_view(), name='connect_wallet_activate'),

    path('connect-wallet-refresh/', ConnectWalletRefreshView.as_view(), name='connect_wallet_refresh'),

    path('transfers/', TransferListAPIView.as_view(), name='transfers'),
    path('payouts/', PayoutListAPIView.as_view(), name='payouts'),

]
