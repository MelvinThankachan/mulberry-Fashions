from django.shortcuts import render, redirect
from product.models import Category, Product, ProductImage, Inventory
from accounts.models import Vendor
from django.utils.text import slugify

# Create your views here.


def vendor_login_required(func):
    """
    Custom login required decorator to check if the user is authenticated and a vendor.
    """

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_vendor:
            return redirect("vendor_login")
        return func(request, *args, **kwargs)

    return wrapper


@vendor_login_required
def dashboard(request):
    title = "Vendor Dashboard"
    products = Product.objects.filter(vendor=request.user).prefetch_related("product_images")
    for product in products:
        primary_image = product.product_images.filter(priority=1).first()
        product.primary_image = primary_image

    context = {"products": products, "title": title}

    return render(request, "vendor/vendor-dashboard.html", context)


@vendor_login_required
def add_product(request):

    if request.method == "POST":
        # Getting the product details
        brand_name = request.POST.get("brand_name").title()
        product_name = request.POST.get("product_name").title()
        description = request.POST.get("description")
        main_category_name = request.POST.get("main_category")

        # Making a list of the product images
        product_images = []
        for i in range(1, 7):
            field_name = f"product_image_{i}"
            if field_name in request.FILES:
                product_image = request.FILES.get(field_name)
                if product_image:
                    product_images.append(product_image)

        # Getting the price and stock of each size
        s_price = request.POST.get("s_price")
        s_stock = request.POST.get("s_stock")
        m_price = request.POST.get("m_price")
        m_stock = request.POST.get("m_stock")
        l_price = request.POST.get("l_price")
        l_stock = request.POST.get("l_stock")
        xl_price = request.POST.get("xl_price")
        xl_stock = request.POST.get("xl_stock")

        # Creating the new product
        main_category = Category.objects.get(name=main_category_name)
        vendor = Vendor.objects.get(email=request.user)
        slug_string = f"{brand_name} {product_name}"
        slug = slugify(slug_string)
        suffix = 2
        while Product.objects.filter(slug=slug).exists():
            slug = slugify(f"{slug_string}-{suffix}")
            suffix += 1

        new_product = Product.objects.create(
            brand_name=brand_name,
            name=product_name,
            description=description,
            main_category=main_category,
            vendor=vendor,
            slug=slug,
        )

        # Storing product images
        priority = 1
        for image in product_images:
            new_product_image = ProductImage.objects.create(
                product=new_product, image=image, priority=priority
            )
            priority += 1

        # Creating product inventory
        size_price_stock = [
            ("S", s_price, s_stock),
            ("M", m_price, m_stock),
            ("L", l_price, l_stock),
            ("XL", xl_price, xl_stock),
        ]

        for size, price, stock in size_price_stock:
            inventory = Inventory.objects.create(
                product=new_product, size=size, price=price, stock=stock
            )

        return redirect("vendor_dashboard")

    categories = Category.objects.all()
    title = "New Product"
    context = {"categories": categories, "title": title}

    return render(request, "vendor/add-product.html", context)
