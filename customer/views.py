from django.shortcuts import render, redirect
from accounts.models import Customer
from django.http import HttpResponse, HttpResponseBadRequest
from .models import Cart, CartItem, Address, Order, OrderItem
from product.models import Product, Inventory
from .utils import list_of_states_in_india
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import logout
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse


def customer_login_required(func):
    """
    Custom login required decorator to check if the user is authenticated and a customer.
    """

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_customer:
            target_url = request.build_absolute_uri()
            request.session["customer_target_url"] = target_url
            return redirect("customer_login")
        return func(request, *args, **kwargs)

    return wrapper


# Customer Profile Session


@customer_login_required
def dashboard(request):
    customer = Customer.objects.get(id=request.user.id)
    orders = (
        Order.objects.filter(
            customer=customer,
        )
        .annotate(total_quantity=Sum("items__quantity"))
        .order_by("-created_at")
    )[:5]

    for order in orders:
        order.order_items = OrderItem.objects.filter(order=order)
        for order_item in order.order_items:
            print(order_item)

    try:
        customer.address = Address.objects.get(customer=customer, is_default=True)
    except:
        pass

    context = {"customer": customer, "orders": orders}
    return render(request, "customer/customer-dashboard.html", context)


@customer_login_required
def address(request):
    customer = Customer.objects.get(id=request.user.id)
    addresses = Address.objects.filter(customer=customer)
    context = {"customer": customer, "addresses": addresses}
    return render(request, "customer/customer-address.html", context)


@customer_login_required
def profile(request):
    customer = Customer.objects.get(id=request.user.id)
    context = {"customer": customer}
    return render(request, "customer/customer-profile.html", context)


@customer_login_required
def edit_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name").title()
        last_name = request.POST.get("last_name").title()
        mobile = request.POST.get("mobile")

        customer = Customer.objects.get(id=request.user.id)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.mobile = mobile
        customer.save()

    return redirect("customer_profile")


@customer_login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        customer = Customer.objects.get(id=request.user.id)

        if not customer.check_password(current_password):
            error_message = "The current password you entered is incorrect."
            messages.error(request, error_message)
            return redirect("change_password")

        if password1 != password2:
            error_message = "The new passwords do not match. Please try again."
            messages.error(request, error_message)
            return redirect("change_password")

        customer.set_password(password1)
        customer.save()
        logout(request)
        success_message = "Your password has been successfully changed. Please Login"
        messages.success(request, success_message)
        return redirect("customer_profile")

    return render(request, "customer/change-password.html")


@customer_login_required
def new_address(request):
    if request.method == "POST":
        name = request.POST.get("name").title()
        pincode = request.POST.get("pincode")
        mobile = request.POST.get("mobile")
        building = request.POST.get("building").title()
        street = request.POST.get("street").title()
        city = request.POST.get("city").title()
        district = request.POST.get("district").title()
        state = request.POST.get("state").title()
        customer = Customer.objects.get(id=request.user.id)
        address_parts = [
            name,
            building,
            street,
            f"{district}, {state}",
            pincode,
            f"Mobile: {mobile}",
        ]
        if city:
            address_parts.insert(3, city)
        address_text = "\n".join(address_parts)

        if not all([name, pincode, mobile, building, street, district, state]):
            messages.error(request, "Please fill in all required fields.")
            return redirect("new_address")

        new_address = Address.objects.create(
            customer=customer,
            name=name,
            pincode=pincode,
            mobile_number=mobile,
            building=building,
            street=street,
            city=city,
            district=district,
            state=state,
            address_text=address_text,
        )

        if Address.objects.filter(customer=customer).count() == 1:
            new_address.is_default = True

        if "checkout_submit" in request.POST:
            return redirect("checkout")
        return redirect("customer_address")

    context = {"states": list_of_states_in_india}
    return render(request, "customer/address_form.html", context)


@customer_login_required
def edit_address(request, address_id):
    address = Address.objects.get(id=address_id)
    if request.method == "POST":
        name = request.POST.get("name").title()
        pincode = request.POST.get("pincode")
        mobile = request.POST.get("mobile")
        building = request.POST.get("building").title()
        street = request.POST.get("street").title()
        city = request.POST.get("city").title()
        district = request.POST.get("district").title()
        state = request.POST.get("state").title()
        customer = Customer.objects.get(id=request.user.id)
        address_parts = [
            name,
            building,
            street,
            f"{district}, {state}",
            f"Pincode - {pincode}",
            f"Mobile: {mobile}",
        ]
        if city:
            address_parts.insert(3, city)
        address_text = "\n".join(address_parts)

        address.customer = customer
        address.name = name
        address.pincode = pincode
        address.mobile_number = mobile
        address.building = building
        address.street = street
        address.city = city
        address.district = district
        address.state = state
        address.address_text = address_text
        address.save()

        return redirect("customer_address")

    context = {"address": address, "states": list_of_states_in_india}
    return render(request, "customer/address_form.html", context)


@customer_login_required
def remove_address(request, address_id):
    address = Address.objects.get(id=address_id)
    address.delete()

    return redirect("customer_address")


@customer_login_required
def default_address(request, address_id):
    address = Address.objects.get(id=address_id)

    try:
        address_default = Address.objects.get(is_default=True)
        address_default.is_default = False
        address_default.save()
    except Exception as e:
        print(e)

    address.is_default = True
    address.save()

    return redirect("customer_address")


@customer_login_required
def orders(request):
    customer = Customer.objects.get(id=request.user.id)
    orders = (
        Order.objects.filter(customer=customer)
        .annotate(total_quantity=Sum("items__quantity"))
        .order_by("-created_at")
    )

    for order in orders:
        order.order_items = OrderItem.objects.filter(order=order)

        for order_item in order.order_items:
            order_item.product.primary_image = order_item.product.product_images.filter(
                priority=1
            ).first()

    context = {"customer": customer, "orders": orders}
    return render(request, "customer/customer-orders.html", context)


@customer_login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    for order_item in order_items:
        if order_item.status != "cancelled":
            order_item.status = "cancelled"
            order_item.inventory.stock += order_item.quantity
            order_item.inventory.save()
            order_item.save()

    order.status = "cancelled"
    order.save()

    return redirect("customer_orders")


def cancel_order_item(request, order_item_id):
    order_item = OrderItem.objects.get(id=order_item_id)

    if order_item.status != "cancelled":
        order_item.status = "cancelled"
        order_item.inventory.stock += order_item.quantity
        order_item.inventory.save()
        order_item.save()

    return redirect("customer_orders")


# Customer Cart Session


@customer_login_required
def cart(request):
    customer = Customer.objects.get(id=request.user.id)
    cart, cart_created = Cart.objects.get_or_create(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    total_amount = 0

    for cart_item in cart_items:
        cart_item.product.primary_image = cart_item.product.product_images.filter(
            priority=1
        ).first()

        total_amount += cart_item.quantity * cart_item.inventory.price

    cart.total_amount = total_amount

    context = {"customer": customer, "cart_items": cart_items, "cart": cart}
    return render(request, "customer/cart.html", context)


@customer_login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        print(request.POST)
        customer = Customer.objects.get(email=request.user.email)
        product = Product.objects.get(pk=product_id)
        cart, cart_created = Cart.objects.get_or_create(customer=customer)
        quantity = int(request.POST.get("product-quantity"))
        size = request.POST.get("product-size")
        inventory = Inventory.objects.get(product=product, size=size)

        if quantity > inventory.stock:
            error_message = (
                f"Only {inventory.stock} item(s) available in stock for this size."
            )
            messages.error(request, error_message)
            return redirect("product_page", slug=product.slug)

        cart_item, cart_item_created = CartItem.objects.get_or_create(
            cart=cart, product=product, inventory=inventory
        )
        if not cart_item_created:
            if cart_item.quantity + quantity > 10:
                cart_item.quantity = 10
            else:
                cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    return redirect("cart")


@customer_login_required
def update_cart_item(request, cart_item_id):
    if request.method == "POST":
        cart_item = CartItem.objects.get(id=cart_item_id)
        quantity = int(request.POST.get("product-quantity"))
        size = request.POST.get("product-size")
        inventory = Inventory.objects.get(product=cart_item.product, size=size)

        cart_item.quantity = quantity
        cart_item.inventory = inventory
        cart_item.save()

    return redirect("cart")


@customer_login_required
def remove_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)

    cart_item.delete()

    return redirect("cart")


@customer_login_required
def checkout(request):
    customer = Customer.objects.get(id=request.user.id)
    cart, cart_created = Cart.objects.get_or_create(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    total_amount = 0

    if not cart_items:
        return redirect("cart")

    for cart_item in cart_items:
        cart_item.product.primary_image = cart_item.product.product_images.filter(
            priority=1
        ).first()

        total_amount += cart_item.quantity * cart_item.inventory.price

    cart.total_amount = total_amount

    addresses = Address.objects.filter(customer=customer)

    context = {
        "customer": customer,
        "cart_items": cart_items,
        "cart": cart,
        "addresses": addresses,
        "states": list_of_states_in_india,
    }
    return render(request, "customer/checkout.html", context)


# Customer Payment Session


# RazorPay intergration

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)


@customer_login_required
def razorpay_order_creation(request):

    currency = "INR"
    amount = 3000 * 100

    data = {"amount": amount, "currency": currency}
    razorpay_order = razorpay_client.order.create(data)

    razorpay_order_id = razorpay_order["id"]
    callback_url = request.build_absolute_uri(reverse("razorpay_paymenthandler"))

    context = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_merchant_key": settings.RAZOR_KEY_ID,
        "razorpay_amount": amount,
        "currency": currency,
        "callback_url": callback_url,
    }

    return render(request, "customer/customer-payment.html", context=context)


@csrf_exempt
def razorpay_paymenthandler(request):
    print("handler")
    # Ensure CSRF protection
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid Request Method")

    try:
        # Get the required parameters from the POST request
        payment_id = request.POST.get("razorpay_payment_id", "")
        razorpay_order_id = request.POST.get("razorpay_order_id", "")
        signature = request.POST.get("razorpay_signature", "")
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }

        # Verify the payment signature
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if result:
            return render(request, "customer/customer-payment-success.html")
        else:
            return HttpResponse("Payment Failed: Invalid Signature", status=400)

    except KeyError:
        # Missing required parameters in POST data
        return HttpResponseBadRequest("Missing Parameters")
    except Exception as e:
        # Other exceptions
        error = f"Error processing payment: {str(e)}"
        return HttpResponse(f"Payment Failed {error}", status=500)


# Customer Order Session


@customer_login_required
def create_order(request, address_id):
    customer = Customer.objects.get(id=request.user.id)
    address = Address.objects.get(id=address_id)
    cart = Cart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    total_amount = 0

    for cart_item in cart_items:
        total_amount += cart_item.quantity * cart_item.inventory.price

    cart.total_amount = total_amount

    order = Order.objects.create(
        customer=customer,
        address=address.address_text,
        total_amount=cart.total_amount,
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            inventory=cart_item.inventory,
            quantity=cart_item.quantity,
        )

        cart_item.inventory.stock -= cart_item.quantity
        cart_item.inventory.save()
        cart_item.delete()

    return redirect("customer_orders")


@customer_login_required
def place_order(request):
    if request.method == "POST":
        print(request.POST)
        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method")

        if payment_method == "cod":
            pass
        elif payment_method == "razorpay":
            return redirect("razorpay_order_creation")
        else:
            return HttpResponse("PASS")
