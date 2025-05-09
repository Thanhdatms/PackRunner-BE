from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema_view, extend_schema
from rest_framework import serializers
from users.serializers import UserSerializer

class LoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=15)
    password = serializers.CharField(required=True, max_length=128)

login_schema = extend_schema_view(
    post=extend_schema(
        summary="User login",
        request=LoginRequestSerializer,
        responses={
            200: OpenApiResponse(description= "OTP sent. Please verify to complete login."),
            400: OpenApiResponse(description="Invalid credentials"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, max_length=255)

logout_schema = extend_schema_view(
    post=extend_schema(
        request=LogoutRequestSerializer,
        summary="User logout",
        responses={
            200: OpenApiResponse(description="Logout successful"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

class RegisterRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)
    phone_number = serializers.CharField(required=True, max_length=15)
    email = serializers.EmailField(required=False, max_length=100)
    password = serializers.CharField(required=True, max_length=128)
    date_of_birth = serializers.DateField(required=False)
    group = serializers.CharField(required=False, max_length=50)
    name = serializers.CharField(required=False, max_length=50)

class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="User registered successfully!")
    data = UserSerializer()

register_schema = extend_schema_view(
    post=extend_schema(
        summary="User registration",
        request=RegisterRequestSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(description="Validation failed"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)
    
class VerifyOTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=15)
    otp = serializers.CharField(required=True, max_length=6)

class VerifyOTPDataSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    groups = serializers.ListField(child=serializers.CharField())
    permissions = serializers.ListField(child=serializers.CharField())

class VerifyOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="OTP verified successfully")
    data = VerifyOTPDataSerializer()

verify_opt_schema = extend_schema_view(
    patch=extend_schema(
        summary="Verify OTP",
        request=VerifyOTPRequestSerializer,
        responses={
            200: VerifyOTPResponseSerializer,
            400: OpenApiResponse(description="Invalid OTP"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)