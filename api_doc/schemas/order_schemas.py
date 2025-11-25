from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema_view, extend_schema
from orders.serializers import OrderSerializer, OrderDetailSerializer
from rest_framework import serializers

order_create_schema = extend_schema_view(
    post=extend_schema(
        summary="Create a new order",
        request=OrderSerializer,
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Validation failed"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

class OrderEstimateShippingCostRequest(serializers.Serializer):
    weight = serializers.FloatField()
    size = serializers.CharField()
    receiver_address = serializers.CharField()
    receiver_province = serializers.CharField()
    receiver_district = serializers.CharField()
    receiver_ward = serializers.CharField()

    sender_address = serializers.CharField()
    sender_province = serializers.CharField()
    sender_district = serializers.CharField()
    sender_ward = serializers.CharField()
    
class OrderEstimateShippingCostReponse(serializers.Serializer):
    total_amount = serializers.FloatField()

order_estimate_shipping_cost_schema = extend_schema_view(
    post=extend_schema(
        summary="Estimate shipping cost",
        request= OrderEstimateShippingCostRequest,
        responses={
            200: OpenApiResponse(
                description="Estimated shipping cost",
                response= OrderEstimateShippingCostReponse
            ),
            400: OpenApiResponse(description="Validation failed"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

order_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Get order detail by ID",
        responses={
            200: OrderDetailSerializer,
            404: OpenApiResponse(description="Order not found"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
)

order_list_schema = extend_schema_view(
    get=extend_schema(
        summary="Get all orders",
        responses={
            200: OrderSerializer(many=True),
            500: OpenApiResponse(description="Internal server error")
        }
    )
) 