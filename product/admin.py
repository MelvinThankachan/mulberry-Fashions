from django.contrib import admin
from .models import Category, Product, Inventory

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {"slug": ("name",)}

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'is_available')

class InventoryAdmin(admin.ModelAdmin):
    list_display = ["product_id", "size", "price", "stock"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
