import pyotp
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from . models import Account


def send_otp(request):
    otp_time = 60  # time to enter otp in seconds
    totp = pyotp.TOTP(pyotp.random_base32(), interval=otp_time)
    otp = totp.now()
    request.session["otp_secret_key"] = totp.secret
    valid_time = datetime.now() + timedelta(seconds=otp_time)
    request.session["otp_valid_till"] = valid_time.isoformat()

    # Sending verification email
    email = request.session.get("email")
    account = Account.objects.get(email=email)
    name = account.first_name + " " + account.last_name
    subject = "OTP Verification - mulberry Fashions"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    message = f"""Dear {name},

Thank you for registering with Mulberry Fashions!

Your OTP (One-Time Password) for verification is: {otp}

Please enter this OTP on the verification page to complete the registration process.

If you didn't request this OTP, please ignore this email.

Thanks,
Mulberry Fashions Team"""
    
    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
