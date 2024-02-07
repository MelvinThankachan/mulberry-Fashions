import pyotp
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from . models import Account

def send_otp(request):
    otp_interval = 60  # time to enter otp in seconds
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key, interval=otp_interval)
    otp = totp.now()
    request.session["otp_secret_key"] = secret_key
    request.session["otp_interval"] = otp_interval
    valid_time = datetime.now() + timedelta(seconds=otp_interval)
    request.session["otp_valid_till"] = valid_time.isoformat()

    # Sending verification email
    email = request.session.get("email")
    account = Account.objects.get(email=email)
    name = account.first_name + " " + account.last_name
    subject = "OTP Verification - mulberry Fashions"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    message = f"""
Dear {name},

Welcome to Mulberry Fashions! We're thrilled to have you as part of our community.

To complete your registration and unlock all the exciting features, we need to verify your email address. Please use the OTP (One-Time Password) provided below:

OTP: {otp}

Please enter this OTP on the verification page to finalize your registration. If you didn't request this OTP, please disregard this email.

We're here to make your fashion journey extraordinary. If you have any questions or need assistance, feel free to reach out to our support team.


Best regards,
The mulberry Fashions Team

[Note: This is an automated email. Please do not reply.]"""
    
    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
