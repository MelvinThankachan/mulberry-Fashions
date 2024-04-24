from django.shortcuts import render, redirect, get_object_or_404
from product.models import Category, Product, ProductImage, Inventory
from accounts.models import Vendor
from django.utils.text import slugify
from django.db.models import Sum
from django.core.paginator import Paginator
from customer.models import Order, OrderItem
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.


def vendor_login_required(func):
    """
    Custom login required decorator to check if the user is authenticated and a vendor.
    """

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_vendor:
            target_url = request.build_absolute_uri()
            request.session["vendor_target_url"] = target_url
            return redirect("vendor_login")
        return func(request, *args, **kwargs)

    return wrapper


@vendor_login_required
def dashboard(request):
    title = "Vendor Dashboard"
    products = (
        Product.objects.filter(vendor=request.user)
        .annotate(total_stock=Sum("inventory_sizes__stock"))
        .prefetch_related("product_images")
    )

    products_count = products.count()

    for product in products:
        product.primary_image = product.product_images.filter(priority=1).first()

    # Pagination
    paginator = Paginator(products, 5)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)

    context = {
        "products": paged_products,
        "title": title,
        "products_count": products_count,
    }

    return render(request, "vendor/vendor-dashboard.html", context)


@vendor_login_required
def add_product(request):

    if request.method == "POST":
        # Getting the product details
        brand_name = request.POST.get("brand_name").title()
        product_name = request.POST.get("product_name").title()
        description = request.POST.get("description")
        main_category = request.POST.get("main_category")
        mrp = request.POST.get("mrp")

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
        main_category = Category.objects.get(name=main_category)
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
            mrp=mrp,
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


@vendor_login_required
def edit_product(request, slug):
    product = Product.objects.get(slug=slug)
    categories = Category.objects.all()
    product_images = ProductImage.objects.filter(product=product).order_by("priority")
    inventory = Inventory.objects.filter(product=product)
    images = [product_images[i] if i < len(product_images) else False for i in range(6)]
    product.images = images

    for inv in inventory:
        setattr(product, f"{inv.size.lower()}_price", inv.price)
        setattr(product, f"{inv.size.lower()}_stock", inv.stock)

    if request.method == "POST":
        brand_name = request.POST.get("brand_name").title()
        product_name = request.POST.get("product_name").title()
        description = request.POST.get("description")
        main_category = request.POST.get("main_category")
        mrp = request.POST.get("mrp")

        s_price = request.POST.get("s_price")
        s_stock = request.POST.get("s_stock")
        m_price = request.POST.get("m_price")
        m_stock = request.POST.get("m_stock")
        l_price = request.POST.get("l_price")
        l_stock = request.POST.get("l_stock")
        xl_price = request.POST.get("xl_price")
        xl_stock = request.POST.get("xl_stock")

        edited_product_images = {
            i: request.FILES.get(f"product_image_{i}")
            for i in range(1, 7)
            if request.FILES.get(f"product_image_{i}")
        }

        # Updating the product details
        product.brand_name = brand_name
        product.name = product_name
        product.description = description
        product.main_category = Category.objects.get(name=main_category)
        product.mrp = mrp
        product.save()

        # Updating the inventory
        for inv in inventory:
            if inv.size == "S":
                inv.price = s_price
                inv.stock = s_stock
            if inv.size == "M":
                inv.price = m_price
                inv.stock = m_stock
            if inv.size == "L":
                inv.price = l_price
                inv.stock = l_stock
            if inv.size == "XL":
                inv.price = xl_price
                inv.stock = xl_stock
            inv.save()

        for i, image_file in edited_product_images.items():
            image, created = ProductImage.objects.get_or_create(
                product=product, priority=i
            )
            image.image = image_file
            image.save()

    title = f"{product.brand_name} {product.name}"
    context = {"categories": categories, "product": product, "title": title}

    return render(request, "vendor/edit-product.html", context)


@vendor_login_required
def vendor_orders(request):
    vendor = Vendor.objects.get(id=request.user.id)

    orders = Order.objects.filter(Q(items__product__vendor=vendor)).distinct()

    order_items = OrderItem.objects.filter(product__vendor = vendor).order_by("-id")

    context = {"orders": orders, "order_items": order_items}
    return render(request, "vendor/vendor-orders.html", context)


@vendor_login_required
def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    vendor = Vendor.objects.get(id=request.user.id)
    order_items = OrderItem.objects.filter(order=order, product__vendor=vendor).order_by("-id")

    for order_item in order_items:
        order_item.product.primary_image = order_item.product.product_images.filter(priority=1).first()
    
    context = {"order": order, "order_items": order_items}

    return render(request, "vendor/vendor-order-details.html", context)


@vendor_login_required
def vendor_order_status(request, order_item_id):
    order_item = OrderItem.objects.get(id=order_item_id)
    if request.method == "POST":
        status = request.POST.get("status")

        if status == "Confirm":
            order_item.status = "confirmed"
        elif status == "Ship":
            order_item.status = "shipped"
        elif status == "Deliver":
            order_item.status = "delivered"
        elif status == "Cancel":
            order_item.status = "cancelled"
            order_item.inventory.stock += order_item.quantity
            order_item.inventory.save()
        
        order_item.save()
    return redirect("vendor_order_details", order_id=order_item.order.id)
