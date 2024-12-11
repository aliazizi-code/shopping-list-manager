from accounts.models import OTPRequest
from django.core.mail import EmailMessage
from django.conf import settings


def send_otp(email):
    otp = OTPRequest.objects.filter(email=email).first()
    if otp:
        email = EmailMessage(
            subject='Code',
            body=otp.password,
            to=email
        )

        try:
            email.send()  # Send the email
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            print(f"Code: {otp.password}")
