from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="vendor_dashboard"),
    path('add-product/', views.add_product, name="add_product"),
    
]