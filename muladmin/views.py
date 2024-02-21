from django.shortcuts import render, redirect
from accounts.models import Customer, Vendor
from django.http import HttpResponse


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
    return render(request, "muladmin/admin-dashboard.html")


@admin_login_required
def customer_list(request):
    customers = Customer.objects.all()
    context = {"customers": customers}
    return render(request, "muladmin/customer-list.html", context=context)


@admin_login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {"vendors": vendors}
    return render(request, "muladmin/vendor-list.html", context=context)


@admin_login_required
def vendor_approval(request, pk):
    vendor = Vendor.objects.get(pk=pk)
    vendor.approved = not vendor.approved
    vendor.save()

    return redirect("vendor_list")
