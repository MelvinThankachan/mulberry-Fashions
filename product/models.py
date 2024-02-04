from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="images/categories")
    description = models.TextField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to="images/products")
    is_available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    sizes = (
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    )

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, choices=sizes, default="s")
    stock = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.size

    class Meta:
        verbose_name_plural = "Inventory"
