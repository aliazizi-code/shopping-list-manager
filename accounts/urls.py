from django.urls import path

from accounts import views

urlpatterns = [
    path('request/', views.OTPRequestView.as_view(), name='request'),
    path('verify/', views.OTPVerifyView.as_view(), name='verify'),
]
