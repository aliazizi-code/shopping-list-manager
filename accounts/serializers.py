from rest_framework import serializers

from accounts.models import OTPRequest


class OTPRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequest
        fields = ('email',)


class OTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()


class VerifyOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=6)
