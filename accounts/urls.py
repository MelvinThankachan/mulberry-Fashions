from django.urls import path
from . import views

urlpatterns = [
    # customer account urls
    path("customer-signup/", views.customer_signup, name="customer_signup"),
    path("customer-login/", views.customer_login, name="customer_login"),
    path("customer-logout/", views.customer_logout, name="customer_logout"),

    # Vendor account urls
    path('login/', views.vendor_login, name="vendor_login"),
    path('signup/', views.vendor_signup, name="vendor_signup"),
    path("vendor-logout/", views.vendor_logout, name="vendor_logout"),

    # Account activation urls
    path("customer-activation/", views.customer_activation, name="customer_activation"),
    path("otp-view/", views.otp_view, name="otp_view"),
]
