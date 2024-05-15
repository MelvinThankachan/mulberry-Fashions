from django.db import models
from accounts.models import Customer


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    minimum_purchase = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class CustomerCoupon(Coupon):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_customer_coupon = models.BooleanField(default=True)


