from django.contrib import admin
from .models import Account, Customer, Vendor
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class AccountAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "last_login",
        "is_active",
    )
    list_display_links = ("email",)
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "last_login",
        "is_active",
    )
    list_display_links = ("email",)
    readonly_fields = ("last_login", "date_joined", 'password')


admin.site.register(Account, AccountAdmin)
admin.site.register(Customer, UserAdmin)
admin.site.register(Vendor, UserAdmin)
