from django.shortcuts import render, redirect
from accounts.models import Customer, Vendor
from product.models import Category, Product


def admin_login_required(func):
    """
    Custom login required decorator to check if the user is authenticated and a superadmin.
    """

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superadmin:
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
    context = {"customers": customers, "current_page": current_page, "title": title}
    return render(request, "muladmin/customer-list.html", context=context)


@admin_login_required
def vendor_list(request):
    title = "Vendors"
    current_page = "vendor_list"
    vendors = Vendor.objects.all()
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
    for category in categories:
        count = Product.objects.filter(main_category=category).count()
        category.count = count
    context = {"categories": categories, "title": title, "current_page": current_page}
    return render(request, "muladmin/category-list.html", context)
