from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts import serializers
from accounts.models import OTPRequest, User
from utils.send_otp import send_otp


class OTPRequestView(APIView):
    serializer_class = serializers.OTPRequestSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            otp_request, created = OTPRequest.objects.get_or_create(email=data['email'])
            otp_request.refresh(data) if not created else None
            send_otp(data)
            return Response(status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    serializer_class = serializers.VerifyOTPRequestSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        otp_request = OTPRequest()

        if serializer.is_valid():
            data = serializer.validated_data
            if otp_request.is_valid(data):
                otp_request.refresh(data)
                return Response(data=self._handle_login(data), status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_login(self, data):
        user, created = User.objects.get_or_create(email=data['email'])
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created
        }
