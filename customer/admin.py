from django.contrib import admin
from .models import Cart, CartItem, Address, Order, OrderItem

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)