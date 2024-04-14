from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Customer, Vendor, Account
from product.models import Category, Product, Inventory, ProductImage
from customer.models import OrderItem
from django.utils.text import slugify
from django.contrib import messages
from django.http import HttpResponse


def admin_login_required(func):
    """
    Custom login required decorator to check if the user is authenticated and a superadmin.
    """

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superadmin:
            target_url = request.build_absolute_uri()
            request.session['admin_target_url'] = target_url
            return redirect("admin_login")
        return func(request, *args, **kwargs)

    return wrapper


@admin_login_required
def admin_dashboard(request):
    title = "Dashboard"
    current_page = "admin_dashboard"
    context = {"current_page": current_page, "title": title}
    return render(request, "muladmin/admin-dashboard.html", context)


@admin_login_required
def customer_list(request):
    title = "Customers"
    current_page = "customer_list"
    customers = Customer.objects.all()
    request.session["selection"] = "all"

    # Filter function
    if request.method == "POST":
        filter_option = request.POST.get("filter_option")
        if filter_option == "banned":
            customers = Customer.objects.filter(approved=False)
            request.session["selection"] = "ban"

    context = {"customers": customers, "current_page": current_page, "title": title}
    return render(request, "muladmin/customer-list.html", context=context)


@admin_login_required
def customer_approval(request, pk):
    customer = Customer.objects.get(pk=pk)
    customer.approved = not customer.approved
    customer.save()

    return redirect("customer_list")


@admin_login_required
def vendor_list(request):
    title = "Vendors"
    current_page = "vendor_list"
    vendors = Vendor.objects.all()
    request.session["selection"] = "all"

    # Filter function
    if request.method == "POST":
        filter_option = request.POST.get("filter_option")
        if filter_option == "waiting_approval":
            vendors = Vendor.objects.filter(approved=False)
            request.session["selection"] = "waiting_approval"

    context = {"vendors": vendors, "current_page": current_page, "title": title}
    return render(request, "muladmin/vendor-list.html", context=context)


@admin_login_required
def vendor_approval(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    vendor.approved = not vendor.approved
    vendor.save()

    return redirect("vendor_list")


@admin_login_required
def category_list(request):
    title = "Categories"
    current_page = "category_list"
    categories = Category.objects.all().order_by("name")
    request.session["selection"] = "listed_categories"

    for category in categories:
        category.count = category.main_category_products.count()

    if request.method == "POST":
        filter_option = request.POST.get("filter_option")
        if filter_option == "deleted_categories":
            categories = Category.all_objects.filter(is_deleted=True)
            request.session["selection"] = "deleted_categories"
            for category in categories:
                category.count = Product.all_objects.filter(
                    main_category=category
                ).count()

    context = {"categories": categories, "title": title, "current_page": current_page}
    return render(request, "muladmin/category-list.html", context)


@admin_login_required
def add_category(request):
    title = "New Category"
    current_page = "add_category"

    if request.method == "POST":
        category_name = request.POST.get("category_name").title()
        category_description = request.POST.get("category_description")
        category_image = request.FILES.get("category_image")
        slug = slugify(category_name)

        if Category.objects.filter(name=category_name).exists():
            error_message = "Category already exists"
            messages.error(request, error_message)
            return redirect("add_category")

        # Creating a new category
        new_category = Category.objects.create(
            name=category_name,
            description=category_description,
            image=category_image,
            slug=slug,
        )
        return redirect("category_list")

    context = {"title": title, "current_page": current_page}
    return render(request, "muladmin/category-form.html", context)


@admin_login_required
def edit_category(request, slug):
    title = f"{slug.capitalize()} | Edit Category"
    category = Category.objects.get(slug=slug)
    image_url = category.image.url

    if request.method == "POST":
        category_name = request.POST.get("category_name").title()
        category_description = request.POST.get("category_description")
        category_image = request.FILES.get("category_image")
        new_slug = slugify(category_name)

        if Category.objects.filter(name=category_name).exists():
            error_message = "Category already exists"
            messages.error(request, error_message)
            return redirect("edit_category", slug=slug)

        # Updating the category
        category.name = category_name
        category.description = category_description
        category.slug = new_slug
        if category_image:
            category.image = category_image
        category.save()
        return redirect("category_list")

    context = {"title": title, "category": category, "image_url": image_url}
    return render(request, "muladmin/category-form.html", context)


@admin_login_required
def delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # Soft deleting products related to the category
    for product in category.main_category_products.all():
        product.delete()

    # Soft deleting category
    category.delete()

    return redirect("category_list")


@admin_login_required
def restore_category(request, slug):
    category = Category.all_objects.get(slug=slug)
    products = Product.all_objects.filter(main_category=category)

    for product in products:
        product.restore()

    category.restore()

    return redirect("category_list")


@admin_login_required
def product_list(request):
    title = "Products"
    current_page = "product_list"
    products = Product.objects.all()
    request.session["selection"] = "all"

    # Filter function
    if request.method == "POST":
        filter_option = request.POST.get("filter_option")
        if filter_option == "awaiting_listing":
            products = Product.objects.filter(approved=False)
            request.session["selection"] = "awaiting_listing"
        elif filter_option == "listed_products":
            products = Product.objects.filter(approved=True)
            request.session["selection"] = "listed_products"

    for product in products:
        inventory = Inventory.objects.filter(product=product)
        total_stock = 0
        for inv in inventory:
            total_stock += inv.stock
        product.total_stock = total_stock

    context = {"products": products, "current_page": current_page, "title": title}
    return render(request, "muladmin/product-list.html", context=context)


@admin_login_required
def product_approval(request, pk):
    product = Product.objects.get(pk=pk)
    product.approved = not product.approved
    product.save()

    return redirect("product_list")


@admin_login_required
def add_account(request):
    title = "Add account"
    current_page = "add_account"
    context = {"title": title, "current_page": current_page}

    if request.method == "POST":
        first_name = request.POST.get("first_name").title()
        last_name = request.POST.get("last_name").title()
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        account_type = request.POST.get("account_type")

        if Account.objects.filter(email=email).exists():
            error_message = (
                "Email already registered. Please log in or use a different email."
            )
            messages.error(request, error_message)

        elif account_type == "vendor":
            try:
                # Creating Vendor
                vendor = Vendor.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
                vendor.is_vendor = True
                vendor.is_active = True
                vendor.save()
            except Exception as e:
                error_message = "Something went wrong, please try again"
                messages.error(request, error_message)

        elif account_type == "customer":
            try:
                # Creating customer
                customer = Customer.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
                customer.is_customer = True
                customer.is_active = True
                customer.approved = True
                customer.save()
            except Exception as e:
                error_message = "Something went wrong, please try again"
                messages.error(request, error_message)

    return render(request, "muladmin/add-account.html", context)


@admin_login_required
def order_list(request):
    title = "Orders"
    current_page = "order_list"
    order_items = OrderItem.objects.all()
    request.session["selection"] = "all"

    context = {"order_items": order_items, "current_page": current_page, "title": title}
    return render(request, "muladmin/order-list.html", context=context)