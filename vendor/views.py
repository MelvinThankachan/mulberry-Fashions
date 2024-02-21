from django.shortcuts import render, redirect
from product.models import Category
from django.contrib import messages

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
    return render(request, "vendor/vendor-dashboard.html")


@vendor_login_required
def add_product(request):

    if request.method == "POST":
        print(request.POST)

    # if request.method == "GET":
    #     # We're deleting existing session keys if there is any.
    #     request.session.pop("brand_name", None)
    #     request.session.pop("product_name", None)
    #     request.session.pop("description", None)
    #     request.session.pop("main_category", None)
    #     request.session.pop("step", None)
    #     request.session.pop("product_images", None)


    if request.method == "POST" and "step_1_button" in request.POST:
        brand_name = request.POST.get("brand_name")
        product_name = request.POST.get("product_name")
        description = request.POST.get("description")
        main_category = request.POST.get("main_category")

        request.session["brand_name"] = brand_name
        request.session["product_name"] = product_name
        request.session["description"] = description
        request.session["main_category"] = main_category

        if main_category is None:
            category_error_message = "Please select a category"
            messages.error(request, category_error_message)
        else:
            request.session["step"] = 2

    if request.method == "POST" and "step_2_button" in request.POST:
        product_images = {}
        for i in range(1, 7):
            field_name = f"product_image_{i}"
            if field_name in request.POST and request.POST[field_name]:
                product_images[field_name] = request.POST[field_name]
                print(field_name)

        request.session["product_images"] = product_images
        request.session["step"] = 3


    categories = Category.objects.all()
    context = {"categories": categories}
    print("\n".join(f"Key: {key}, Value: {value}" for key, value in request.session.items()))

    return render(request, "vendor/add-product.html", context)
