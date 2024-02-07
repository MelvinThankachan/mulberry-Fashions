from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.



def dashboard(request):

    # Login required to view this page
    if request.user.is_authenticated and request.user.is_vendor:
        return render(request, "vendor/vendor-dashboard.html")
    
    success_message = "Please Login to continue"
    messages.success(request,success_message)
    return redirect("vendor_login")
