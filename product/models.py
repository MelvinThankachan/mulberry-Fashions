from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import Vendor
from mulberry.models import SoftDeleteModel, ApprovedProductManager


class Category(SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="images/categories")
    description = models.TextField(max_length=511, null=True, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(SoftDeleteModel):
    brand_name = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=511, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    main_category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="main_category_products"
    )
    subcategories = models.ManyToManyField(
        Category, related_name="subcategory_products", blank=True
    )
    mrp = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=True, blank=True
    )
    is_available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    approved_objects = ApprovedProductManager()

    def __str__(self):
        return f"{self.brand_name} {self.name}"


class Inventory(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    ]
    product = models.ForeignKey(
        Product, related_name="inventory_sizes", on_delete=models.CASCADE
    )
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default="S")
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.size} size"

    class Meta:
        verbose_name_plural = "Inventory"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="product_images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="images/product_images")
    priority = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Image of {self.product.name}"
