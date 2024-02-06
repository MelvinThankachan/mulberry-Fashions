from django.shortcuts import render
from product.models import Product, Category


# Create your views here.
def home(request):
    title = "Home"
    products = Product.objects.filter(is_available=True)[:9]
    categories = Category.objects.all()[:4]
    context = {"products": products, "categories": categories, "title": title}
    return render(request, "home/home.html", context)


def shop(request):
    title = "Shop"
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    context = {"products": products, "categories": categories, "title": title}
    return render(request, "home/shop.html", context)


def product_page(request, pk):
    product = Product.objects.filter(pk=pk)
    title = product.name
    context = {"product": product}
    return render(request, "home/product-details.html", context)