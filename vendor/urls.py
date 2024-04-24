from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="vendor_dashboard"),
    path('add-product/', views.add_product, name="add_product"),
    path('edit-product/<slug>/', views.edit_product, name="edit_product"),
    path('orders/', views.vendor_orders, name="vendor_orders"),
    path('order-item-status/<order_item_id>/', views.vendor_order_status, name="vendor_order_status"),
    path('order-details/<order_id>/', views.order_details, name="vendor_order_details"),
    
]