from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema_view, extend_schema
from users.serializers import User, UserSerializer, AddressSerializer
from rest_framework import serializers

class UserProfileRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=100)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False, max_length=15)
    date_of_birth = serializers.DateField(required=False)

user_profile_schema = extend_schema_view(
    get=extend_schema(
        summary="Get user profile",
        responses={
            200: UserSerializer,
            404: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(description="Internal server error")
        }
    ),
    put=extend_schema(
        summary="Update user profile",
        request=UserProfileRequestSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation failed"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

address_schema = extend_schema_view(
    get=extend_schema(
        summary="Get all user address",
        responses={
            200: AddressSerializer(many=True),
            404: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(description="Internal server error")
        }
    ),
    post=extend_schema(
        summary="Create user address",
        request=AddressSerializer,
        responses={
            201: AddressSerializer,
            400: OpenApiResponse(description="Validation failed"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

address_detail_schema = extend_schema_view(
    delete=extend_schema(
        summary="Delete user address",
        responses={
            204: OpenApiResponse(description="Address deleted successfully"),
            404: OpenApiResponse(description="Address not found"),
            500: OpenApiResponse(description="Internal server error")
        }
    ),  
    patch=extend_schema(
        summary="Update user address",
        request=AddressSerializer,
        responses={
            200: AddressSerializer,
            400: OpenApiResponse(description="Validation failed"),
            404: OpenApiResponse(description="Address not found"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

