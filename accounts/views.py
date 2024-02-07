from django.shortcuts import render, redirect
from .models import Customer, Account, Vendor
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .utils import send_otp, pyotp
from datetime import datetime


# Customer Login, Signup and logout views


def customer_signup(request):

    if request.method == "POST":
        first_name = request.POST.get("first_name").capitalize()
        last_name = request.POST.get("last_name").capitalize()
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            error_message = "Passwords don't match. Please try again."
            messages.error(request, error_message)
            return redirect("customer_signup")

        if Customer.objects.filter(email=email).exists():
            error_message = (
                "Email already registered. Please log in or use a different email."
            )
            messages.error(request, error_message)
        else:
            try:
                # Creating Customer
                customer = Customer.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
                customer.is_customer = True
                customer.save()
                success_message = "Please verify your email."
                messages.success(request, success_message)

                # Customer activation
                request.session["email"] = customer.email
                request.session["target_page"] = "customer_login"
                request.session["account_type"] = "customer"
                return redirect("otp_view")

            except Exception as e:

                # Checking if the email is already registered but not as a customer profile
                if Account.objects.filter(email=email).exists():
                    error_message = "Email already registered and not associated with a customer account. Please use a different email."
                    messages.error(request, error_message)
                else:
                    error_message = "Something went wrong, please try again"
                    messages.error(request, error_message)

    title = "Signup"
    context = {"title": title}
    return render(request, "accounts/customer-signup.html", context)


def customer_login(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            error_message = "Account not found. Please check your email and try again."
            messages.error(request, error_message)
            return redirect("customer_login")

        if not customer.is_active:
            request.session["email"] = email
            request.session["target_page"] = "customer_login"
            request.session["account_type"] = "customer"

            error_message = "Your email is not verified. Please verify your email to login."
            messages.error(request, error_message)
            return redirect("otp_view")

        authenticated_user = authenticate(email=email, password=password)
        if authenticated_user is None:
            error_message = "Invalid password. Please try again."
            messages.error(request, error_message)
            return redirect("customer_login")

        login(request, authenticated_user)
        return redirect("home")

    title = "LogIn"
    context = {"title": title}
    return render(request, "accounts/customer-login.html", context)


def customer_logout(request):
    logout(request)
    return redirect("home")


# Vendor login, signup and login views


def vendor_signup(request):

    if request.method == "POST":
        first_name = request.POST.get("first_name").capitalize()
        last_name = request.POST.get("last_name").capitalize()
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            error_message = "Passwords don't match. Please try again."
            messages.error(request, error_message)
            return redirect("vendor_signup")

        if Vendor.objects.filter(email=email).exists():
            error_message = (
                "Email already registered. Please log in or use a different email."
            )
            messages.error(request, error_message)
        else:
            try:
                # Creating Vendor
                vendor = Vendor.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
                vendor.is_vendor = True
                vendor.save()
                success_message = "Please verify your email."
                messages.success(request, success_message)

                # Customer activation
                request.session["email"] = vendor.email
                request.session["target_page"] = "vendor_login"
                request.session["account_type"] = "vendor"
                return redirect("otp_view")

            except Exception as e:

                # Checking if the email is already registered but not as a vendor profile
                if Account.objects.filter(email=email).exists():
                    error_message = "Email already registered and not associated with a vendor account. Please use a different email."
                    messages.error(request, error_message)
                else:
                    error_message = "Something went wrong, please try again"
                    messages.error(request, error_message)

    title = "Vendor Signup"
    context = {"title": title}
    return render(request, "accounts/vendor-signup.html", context)


def vendor_login(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            vendor = Vendor.objects.get(email=email)
        except Vendor.DoesNotExist:
            error_message = "Account not found. Please check your email and try again."
            messages.error(request, error_message)
            return redirect("vendor_login")

        if not vendor.is_active:
            request.session["email"] = email
            request.session["target_page"] = "vendor_login"
            request.session["account_type"] = "vendor"

            error_message = "Your email is not verified. Please verify your email to login."
            messages.error(request, error_message)
            return redirect("otp_view")

        authenticated_user = authenticate(email=email, password=password)
        if authenticated_user is None:
            error_message = "Invalid password. Please try again."
            messages.error(request, error_message)
            return redirect("vendor_login")

        login(request, authenticated_user)
        return redirect("vendor_dashboard")

    title = "Vendor LogIn"
    context = {"title": title}
    return render(request, "accounts/vendor-login.html", context)


def vendor_logout(request):
    logout(request)
    return redirect("vendor_dashboard")


# Account activation views


def otp_view(request):
    send_otp(request)
    return redirect("customer_activation")


def customer_activation(request):
    email = request.session.get("email")
    otp_secret_key = request.session.get("otp_secret_key")
    otp_interval = request.session.get("otp_interval")
    otp_valid_till = datetime.fromisoformat(request.session.get("otp_valid_till"))
    time_left = round((otp_valid_till - datetime.now()).total_seconds())

    if request.method == "POST":
        otp = request.POST.get("otp")

        if otp_secret_key and otp_valid_till is not None:
            if otp_valid_till > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=int(otp_interval))
                if totp.verify(otp):
                    # Activating account
                    account = Account.objects.get(email=email)
                    account.is_active = True
                    account.save()

                    # Removing OTP cookies from session
                    request.session.pop("otp_secret_key", None)
                    request.session.pop("otp_valid_till", None)
                    target_page = request.session.get("target_page")

                    success_message = "Your email is verified. Please Login now"
                    messages.success(request, success_message)

                    # redirecting to targeted page
                    return redirect(target_page)
                else:
                    error_message = "Invalid OTP"
                    messages.error(request, error_message)
            else:
                error_message = "OTP entry timed out. To receive a new OTP, please click the 'Resend OTP' button below."
                messages.error(request, error_message)
        else:
            error_message = "Something went wrong. Please try again."
            messages.error(request, error_message)

    context = {"time_left": time_left}
    account_type = request.session.get("account_type")

    # Rendering the page according the account type
    if account_type == "customer":
        return render(request, "accounts/customer-activation.html", context)
    if account_type == "vendor":
        return render(request, "accounts/vendor-activation.html", context)
