from django.shortcuts import render, redirect
from product.models import Product, Category, ProductImage, Inventory


# Create your views here.
def home(request):
    title = "Home"
    products = Product.objects.filter(is_available=True)[:9]
    for product in products:
        primary_image = product.product_images.filter(priority=1).first()
        product.primary_image = primary_image
    for product in products:
        small_size = product.inventory_sizes.get(size="S")
        small_size_price = small_size.price
        product.price = small_size_price
    categories = Category.objects.all()[:4]
    context = {"products": products, "categories": categories, "title": title}
    return render(request, "home/home.html", context)

def shop(request):
    title = "Shop"
    products = Product.objects.all()
    for product in products:
        primary_image = product.product_images.filter(priority=1).first()
        product.primary_image = primary_image
    for product in products:
        small_size = product.inventory_sizes.get(size="S")
        small_size_price = small_size.price
        product.price = small_size_price
    categories = Category.objects.all()
    context = {"products": products, "categories": categories, "title": title}
    return render(request, "home/shop.html", context)


def product_page(request, slug):
    product = Product.objects.get(slug=slug)
    product_images = ProductImage.objects.filter(product=product).order_by("priority")
    inventory = Inventory.objects.filter(product=product)
    title = product
    context = {"product": product, "inventory": inventory, "product_images": product_images, 'title': title}
    return render(request, "home/product-page.html", context)