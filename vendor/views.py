from django.shortcuts import render, redirect
# Create your views here.



def dashboard(request):
    # Login required to view this page
    if request.user.is_authenticated and request.user.is_vendor:
        return render(request, "vendor/vendor-dashboard.html")
    
    return redirect("vendor_login")