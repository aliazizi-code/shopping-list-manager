from accounts.models import OTPRequest


def send_otp(data):
    otp = OTPRequest.objects.filter(email=data['email']).first()
    if otp:
        print(f"Code: {otp.password}")
