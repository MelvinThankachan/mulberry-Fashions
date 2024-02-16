from django.shortcuts import render, redirect
from accounts.models import Customer,Vendor


def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("admin_login")
    return render(request, "muladmin/admin-dashboard.html")


def customer_list(request):
    customers = Customer.objects.all()
    context = {"customers": customers}
    return render(request, "muladmin/customer-list.html", context=context)


def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {"vendors": vendors}
    return render(request, "muladmin/vendor-list.html", context=context)
