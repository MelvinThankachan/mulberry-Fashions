from django.contrib import admin
from .models import Category, Product, Inventory, ProductImage

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("brand_name","name",)}
    list_display = ("brand_name", "name", "vendor", "is_available")
    list_display_links = ("brand_name", "name")


class InventoryAdmin(admin.ModelAdmin):
    list_display = ["product", "size", "price", "stock"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(ProductImage)
