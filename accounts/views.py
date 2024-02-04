from django.shortcuts import render, redirect
from .models import Customer, Account
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def customer_signup(request):
    title = "Signup"
    context = {"title": title}
    try:
        if request.POST:
            first_name = request.POST.get("first_name").capitalize()
            last_name = request.POST.get("last_name").capitalize()
            email = request.POST.get("email")
            password = request.POST.get("password")

            if Account.objects.filter(email=email).exists():
                error_message = "Oops! It looks like that email address is already registered. Please try signing in, or use a different email address to create a new account."
                messages.error(request, error_message)
                return redirect("customer_signup")
            else:
                # Creating Customer
                customer = Customer.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
            success_message = "Congratulations! Your registration is complete. Welcome to mulberry Fashions! Please Login."
            messages.success(request, success_message)
            return redirect("customer_login")
    except Exception as e:
        error_message = "Something went wrong, please try again"
        messages.error(request, error_message)

    return render(request, "accounts/signup.html", context)


def customer_login(request):
    title = "LogIn"
    context = {"title": title}

    if request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")
        customer = authenticate(email=email, password=password)
        if customer:
            login(request, customer)
            return redirect("home")
        else:
            if not Account.objects.filter(email=email).exists():
                error_message = "Oops! We couldn't find an account with that email address. Please check your email and try again."
            else:
                error_message = "Oops! We couldn't log you in. Please check your password and try again."
            messages.error(request, error_message)
            return redirect("customer_login")

    return render(request, "accounts/login.html", context)


def customer_logout(request):
    logout(request)
    return redirect("home")
