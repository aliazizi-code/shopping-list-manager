from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from utils.generate_otp import generate_otp


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class OTPRequest(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now=True, editable=False)

    def is_valid(self, data):
        current_time = timezone.now()
        return OTPRequest.objects.filter(
            email=data['email'],
            password=data['password'],
            created_at__lt=current_time,
            created_at__gt=current_time - timezone.timedelta(seconds=120)
        ).exists()

    def refresh(self, data):
        otp = OTPRequest.objects.filter(email=data['email']).first()
        if otp:
            otp.password = generate_otp()
            otp.created_at = timezone.now()
            otp.save()
