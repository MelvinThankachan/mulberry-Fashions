from django.shortcuts import render, redirect
import razorpay
from django.conf import settings
from customer.models import Order, Cart, CartItem
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Customer
from django.contrib import messages
from customer.views import create_order


# Customer Payment Session

# RazorPay intergration

# Authorize razorpay client with API Key.

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)


def razorpay_order_creation(request, amount):
    currency = "INR"
    amount = int(amount) * 100

    data = {"amount": amount, "currency": currency, "receipt": str(request.user.id)}
    print(data)
    razorpay_order = razorpay_client.order.create(data)

    razorpay_order_id = razorpay_order["id"]
    callback_url = request.build_absolute_uri(reverse("razorpay_paymenthandler"))

    context = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_merchant_key": settings.RAZOR_KEY_ID,
        "razorpay_amount": amount,
        "actual_amount": amount / 100,
        "currency": currency,
        "callback_url": callback_url,
    }

    return render(request, "customer/customer-payment.html", context=context)


@csrf_exempt
def razorpay_paymenthandler(request):
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
        try:
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result:
                is_order_created = create_order(request)
                print(f"is_order_created: {is_order_created}")
                return render(request, "customer/customer-payment-success.html")
            else:
                error_message = "Payment Failed. Please try again."
                messages.error(request, error_message)
                return redirect("checkout")
        except Exception as e:
            print(e)
            error_message = "Payment Failed. Please try again."
            messages.error(request, error_message)
            return redirect("checkout")

    except KeyError:
        # Missing required parameters in POST data
        return HttpResponseBadRequest("Missing Parameters")
    except Exception as e:
        # Other exceptions
        error = f"Error processing payment: {str(e)}"
        return HttpResponse(f"Payment Failed {error}", status=500)
