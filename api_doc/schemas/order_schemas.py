from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema_view, extend_schema
from orders.serializers import OrderSerializer, OrderDetailSerializer


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

order_detail_schema = extend_schema_view(
    get=extend_schema(
        summary="Get order detail by ID",
        parameters=[
            OpenApiParameter(name='pk', description='Order ID', required=True, type=int)
        ],
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