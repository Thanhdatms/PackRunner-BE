from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import OrderSerializer, ShipmentSerializer, OrderStatusUpdateSerializer, PaymentSerializer, OrderDetailSerializer, OrderStatisticsSerializer
from .models import Order, Shipment
from utils.response import success_response, fail_response
from users.permissions import IsOwnerOrReadOnly

from drf_spectacular.utils import extend_schema
from api_doc.schemas.order_schemas import order_create_schema, order_detail_schema, order_list_schema
# Create your views here.

@extend_schema(tags=['Order'])
@order_create_schema
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = OrderSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(serializer.data, status_code=201)
        except Exception as err:
            return fail_response(error=str(err))

@extend_schema(tags=['Order'])
@order_detail_schema
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, sender=request.user)
            serializer = OrderDetailSerializer(order)
            return success_response(serializer.data)
        except Order.DoesNotExist:
            return fail_response(error="Order not found", status_code=404)
        except Exception as err:
            return fail_response(error=str(err), status_code=500)
     
@extend_schema(
    request=ShipmentSerializer,
    responses=ShipmentSerializer,
    tags=['Order']
)
@order_list_schema
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = Order.objects.filter(sender=request.user).prefetch_related('payments', 'shipments')
            serializer = OrderSerializer(orders, many=True)
            return success_response(serializer.data)
        except Exception as err:
            return fail_response(error=str(err), status_code=500)
        
@extend_schema(
    request=OrderStatusUpdateSerializer,
    responses=OrderStatusUpdateSerializer,
    tags=['Order']
)
class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, sender=request.user)
            serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return success_response(serializer.data)
            
        except Order.DoesNotExist:
            return fail_response(error="Order not found", status_code=404)
        except Exception as err:
            return fail_response(error=err)
        
@extend_schema(
    request=PaymentSerializer,
    responses=PaymentSerializer,
    tags=['Payment']
)   
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = PaymentSerializer(data=request.data, context={'request': request})

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return success_response(serializer.data)

        except Exception as err:
            return fail_response(error=err)
         
@extend_schema(
    request=None,
    responses=OrderStatisticsSerializer,
    tags=['OrderStatistics']
)
class OrderStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            orders = Order.objects.filter(sender=user)

            total_orders = orders.count()
            total_amount = sum(order.total_price for order in orders)

            ordered_orders = orders.filter(order_status='Ordered').count()
            in_transit_orders = orders.filter(order_status='In Transit').count()
            delivered_orders = orders.filter(order_status='Delivered').count()

            return success_response({
                'total_orders': total_orders,
                'total_amount': total_amount,
                'ordered_orders': ordered_orders,
                'in_transit_orders': in_transit_orders,
                'delivered_orders': delivered_orders
            })

        except Exception as err:
            return fail_response(error=str(err), status_code=500)