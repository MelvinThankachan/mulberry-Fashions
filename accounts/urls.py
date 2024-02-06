from django.urls import path
from . import views

urlpatterns = [
    path("customer-signup/", views.customer_signup, name="customer_signup"),
    path("customer-login/", views.customer_login, name="customer_login"),
    path("customer-logout/", views.customer_logout, name="customer_logout"),
    path("customer-activation/", views.customer_activation, name="customer_activation"),
    path("otp-view/", views.otp_view, name="otp_view"),
]
