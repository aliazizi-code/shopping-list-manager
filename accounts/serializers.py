from rest_framework import serializers

from accounts.models import OTPRequest


class OTPRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequest
        fields = ('email', 'request_id')
        read_only_fields = ('request_id',)


class VerifyOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=6)
