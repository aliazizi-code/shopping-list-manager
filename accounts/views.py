from drf_spectacular.utils import extend_schema
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

    @extend_schema(
        request=serializers.OTPRequestSerializer,
        responses={
            200: serializers.OTPResponseSerializer,
            201: serializers.OTPResponseSerializer,
            400: "Invalid Input",
        },
        description="Request an OTP for the provided email."
    )

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            otp_request, created = OTPRequest.objects.get_or_create(email=data['email'])

            otp_request.refresh(data) if not created else None
            send_otp(data['email'])

            response_data = {
                "message": "OTP sent successfully",
                "email": data['email']
            }
            response_serializer = serializers.OTPResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    serializer_class = serializers.VerifyOTPRequestSerializer

    @extend_schema(
        request=serializers.VerifyOTPRequestSerializer,
        responses={
            200: 'Successful login with access and refresh tokens',
            401: 'Unauthorized - Invalid OTP',
            400: 'Invalid Input',
        },
        description="Verify the OTP for the provided email."
    )

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        otp_request = OTPRequest()

        if serializer.is_valid():
            data = serializer.validated_data
            if otp_request and otp_request.is_valid(data):
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
