from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name="admin_dashboard"),
    path('customer-list/', views.customer_list, name="customer_list"),
    path('vendor-list/', views.vendor_list, name="vendor_list"),
    path('vendor-approval/<pk>/', views.vendor_approval, name="vendor_approval"),
    
]
