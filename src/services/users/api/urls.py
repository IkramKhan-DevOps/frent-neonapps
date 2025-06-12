from django.urls import path

from src.services.users.api.views import UserRetrieveUpdateAPIView, UserImageCreateAPIView, UserImageDestroyAPIView, \
    UserAddressRetrieveUpdateAPIView, ServiceProviderRetrieveUpdateAPIView, ServiceProviderInterestCreateAPIView, \
    ServiceProviderSocialMediaRetrieveUpdateDestroyAPIView, ServiceProviderSocialMediaListCreateAPIView, \
    ServiceProviderCertificateDestroyAPIView, \
    ServiceProviderCertificationCreateAPIView, ServiceProviderLanguageCreateAPIView, \
    ServiceProviderLanguageDestroyAPIView, FavoriteServiceDestroyAPIView, FavoriteServiceListCreateAPIView, \
    UserContactListCreateAPIView, UserContactUpdateDestroyAPIView, ServiceProviderInterestDestroyAPIView, \
    ServiceProviderRetrieveAPIView, UserRetrieveAPIView, BlockedUserListCreateAPIView, BlockedUserDestroyAPIView, \
    ReportListCreateApiView, ServiceProviderSocialMediaListAPIView

app_name = "users-api"

"""SERVICE SEEKER URLS"""
urlpatterns = [
    path('v1/profile/', UserRetrieveUpdateAPIView.as_view(), name='user-update'),
    path('v1/profile/<str:pk>/', UserRetrieveAPIView.as_view(), name='user-detail'),
    path('v1/image/', UserImageCreateAPIView.as_view(), name='image-update'),
    path('v1/image/<str:pk>/', UserImageDestroyAPIView.as_view(), name='image-delete'),
    path('v1/address/', UserAddressRetrieveUpdateAPIView.as_view(), name='address-update'),

    path('v1/favorite-service/', FavoriteServiceListCreateAPIView.as_view(), name='favorite-service'),
    path('v1/favorite-service/<str:pk>/', FavoriteServiceDestroyAPIView.as_view(), name='favorite-service-delete'),

    path('v1/contact/', UserContactListCreateAPIView.as_view(), name='user-contact'),
    path('v1/contact/<str:pk>/', UserContactUpdateDestroyAPIView.as_view(), name='user-contact-delete'),
]

"""SERVICE PROVIDER URLS"""

urlpatterns += [
    path('v1/service-provider/interest/', ServiceProviderInterestCreateAPIView.as_view(),
         name='service-provider-interest'),
    path('v1/service-provider/interest/<str:pk>/', ServiceProviderInterestDestroyAPIView.as_view(),
         name='service-provider-interest-destroy'),
]
urlpatterns += [
    path('v1/service-provider/language/<str:pk>/', ServiceProviderLanguageDestroyAPIView.as_view(),
         name='service-provider-language-destroy'),
    path('v1/service-provider/language/', ServiceProviderLanguageCreateAPIView.as_view(),
         name='service-provider-language'),
]
urlpatterns += [
    path('v1/service-provider/certificate/', ServiceProviderCertificationCreateAPIView.as_view(),
         name='service-provider-certificate'),
    path('v1/service-provider/certificate/<str:pk>/', ServiceProviderCertificateDestroyAPIView.as_view(),
         name='service-provider-certificate-delete'),
]

urlpatterns += [
    path('v1/service-provider/<str:pk>/social-media/', ServiceProviderSocialMediaListAPIView.as_view(),
         name='service-provider-social-media-get'),

    path('v1/service-provider/social-media/', ServiceProviderSocialMediaListCreateAPIView.as_view(),
         name='service-provider-social-media-list-create'),
    path('v1/service-provider/social-media/<str:pk>/', ServiceProviderSocialMediaRetrieveUpdateDestroyAPIView.as_view(),
         name='service-provider-social-media-update-destroy'),
]

urlpatterns += [
    path('v1/service-provider/', ServiceProviderRetrieveUpdateAPIView.as_view(), name='service-provider-update'),
    path('v1/service-provider/<str:pk>/', ServiceProviderRetrieveAPIView.as_view(), name='service-provider-detail'),

]

urlpatterns += [
    path('v1/blocked-users/', BlockedUserListCreateAPIView.as_view(), name='blocked-user'),
    path('v1/blocked-users/<str:pk>/', BlockedUserDestroyAPIView.as_view(), name='blocked-user-delete'),
]

urlpatterns += [
    path('v1/report/', ReportListCreateApiView.as_view(), name='report'),
]
