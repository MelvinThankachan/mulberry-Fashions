from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name="admin_dashboard"),
    path('customer-list/', views.customer_list, name="customer_list"),
    path('customer-approval/<pk>/', views.customer_approval, name="customer_approval"),
    path('vendor-list/', views.vendor_list, name="vendor_list"),
    path('vendor-approval/<pk>/', views.vendor_approval, name="vendor_approval"),
    path('categories/', views.category_list, name="category_list"),
    path('add-category/', views.add_category, name="add_category"),
    path('edit-category/<slug>', views.edit_category, name="edit_category"),
    path('delete-category/<slug>', views.delete_category, name="delete_category"),
    path('restore-category/<slug>', views.restore_category, name="restore_category"),
    path('product-list/', views.product_list, name="product_list"),
    path('product-approval/<pk>/', views.product_approval, name="product_approval"),
    path('add-account/', views.add_account, name="add_account"),
    path('order-list/', views.order_list, name="order_list"),
    path('sales-report/', views.sales_report, name="sales_report"),
]
