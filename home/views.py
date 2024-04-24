from django.shortcuts import render, redirect
from product.models import Product, Category, ProductImage, Inventory
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import F, Sum
from customer.models import OrderItem


# Create your views here.
def home(request):
    title = "Home"
    products = Product.approved_objects.filter(is_available=True)[:9]
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
    sort_by = request.session.get("sort_by", "Relevance")
    selected_category = request.session.get("selected_category", "All Categories")
    selected_brand = request.session.get("selected_brand", "All Brands")

    print(request.GET)
    if "search" in request.GET:
        search_term = request.GET.get("search")
        products = (
            Product.approved_objects.filter(name__icontains=search_term)
            .filter(inventory_sizes__size="S")
            .annotate(price=F("inventory_sizes__price"))
        )
    else:
        products = (
            Product.approved_objects.all()
            .filter(inventory_sizes__size="S")
            .annotate(price=F("inventory_sizes__price"))
        )

    if request.method == "POST":
        selected_category = request.POST.get("selected_category")
        selected_brand = request.POST.get("selected_brand")
        request.session[selected_category] = selected_category
        request.session[selected_brand] = selected_brand
        sort_by = request.POST.get("sort_by")
        request.session[sort_by] = sort_by
        print(f"sortby:{sort_by}\ncategory:{selected_category}\nbrand:{selected_brand}")

        if selected_category != "All Categories":
            category = Category.objects.get(name=selected_category)
            products = (
                Product.approved_objects.filter(main_category=category)
                .filter(inventory_sizes__size="S")
                .annotate(price=F("inventory_sizes__price"))
            )
            
        if selected_brand != "All Brands":
            products = (
                Product.approved_objects.filter(brand_name=selected_brand)
                .filter(inventory_sizes__size="S")
                .annotate(price=F("inventory_sizes__price"))
            )

        if sort_by == "Price Low to High":
            products = products.order_by("price")
        elif sort_by == "Price High to Low":
            products = products.order_by("-price")
        elif sort_by == "New Arrivals":
            products = products.order_by("-created_at")
        elif sort_by == "aA - zZ":
            products = products.order_by("brand_name")
        elif sort_by == "zZ - aA":
            products = products.order_by("-brand_name")
        elif sort_by == "Popularity":
            products = products.annotate(total_quantity_ordered=Sum('orderitem__quantity'))
            products = products.order_by("-total_quantity_ordered")

    for product in products:
        product.primary_image = product.product_images.filter(priority=1).first()

    products = [product for product in products for _ in range(1)]
    paginator = Paginator(products, 6)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)

    categories = Category.objects.all()
    brands = Product.approved_objects.values_list('brand_name', flat=True).distinct()
    context = {
        "products": paged_products,
        "categories": categories,
        "title": title,
        "sort_by": sort_by,
        "selected_category": selected_category,
        "brands": brands,
    }
    return render(request, "home/shop.html", context)


def product_page(request, slug):
    product = Product.approved_objects.get(slug=slug)
    product_images = ProductImage.objects.filter(product=product).order_by("priority")
    inventory = Inventory.objects.filter(product=product, stock__gt=0)
    title = product
    context = {
        "product": product,
        "inventory": inventory,
        "product_images": product_images,
        "title": title,
    }
    return render(request, "home/product-page.html", context)
