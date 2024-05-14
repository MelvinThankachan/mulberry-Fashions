from django.db import models


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
