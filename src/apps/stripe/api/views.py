from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe import AuthenticationError

from src.apps.stripe.api.serializers import TransferSerializer, PayoutSerializer, ConnectWalletSerializer
from src.apps.stripe.bll import stripe_connect_account_create, stripe_connect_account_link, get_connect_wallet_balance
from src.apps.stripe.models import Transfer, Payout


class ConnectWalletCreateAPIView(APIView):
    """
    Create a new Wallet for the User
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_stripe_connected():
            return Response({'detail': 'You have already connected your wallet'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            error, account = stripe_connect_account_create(user)
            if error:
                return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationError as e:
            return Response({'detail': f'Authentication error: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Your wallet has been connected successfully'},
                        status=status.HTTP_200_OK)


class ConnectWalletVisitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        wallet = user.get_user_wallet()

        # Check if the user has connected their wallet
        if not user.is_stripe_connected() or not wallet.is_stripe_account_active():
            return Response(
                {"detail": "You have not Activate/Connected your Connect wallet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate Stripe connect link
        error, url = stripe_connect_account_link(wallet.stripe_account_id)

        if error:
            return Response(
                {"detail": f"Stripe Error: {error}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Success — return the URL to frontend so it can redirect
        return Response(
            {"connect_url": url},
            status=status.HTTP_200_OK
        )


class ConnectWalletActivateAPIView(APIView):
    """
    Visit the Wallet Dashboard
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        wallet = user.get_user_wallet()
        if  wallet.is_stripe_account_active() and user.is_stripe_connected():
            return Response(
                {"detail": "Your Connect wallet is already connected and Activated."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            error, url = stripe_connect_account_link(wallet.stripe_account_id)
            if error:
                return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationError as e:
            return Response({'detail': f'Authentication error: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'url': url}, status=status.HTTP_200_OK)


class ConnectWalletRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.get_user_wallet().is_stripe_account_active():
            get_connect_wallet_balance(request.user)
            return Response({'detail': 'Wallet refreshed successfully'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Connect Wallet is not active'}, status=status.HTTP_400_BAD_REQUEST)


class TransferListAPIView(ListAPIView):
    """
    List all Transfers of user
    """
    model = Transfer
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transfer.objects.filter(user=self.request.user)


class PayoutListAPIView(ListAPIView):
    """
    List all Payouts of user
    """
    model = Payout
    serializer_class = PayoutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payout.objects.filter(user=self.request.user)
