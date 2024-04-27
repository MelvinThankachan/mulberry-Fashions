from django.urls import path
from . import views

urlpatterns = [
    path('razorpay-order-creation/<amount>/', views.razorpay_order_creation, name="razorpay_order_creation"),
	path('razorpay-paymenthandler/', views.razorpay_paymenthandler, name='razorpay_paymenthandler'),
]
