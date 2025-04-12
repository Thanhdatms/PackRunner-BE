from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer, ShipmentSerializer, OrderStatusUpdateSerializer
from .models import Order, Shipment
from utils.response import success_response, fail_response
from users.permissions import IsOwnerOrReadOnly
# Create your views here.

class OrderView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request):
        try:
            serializer = OrderSerializer(data = request.data, context={'request':request})

            serializer.is_valid(raise_exception=True)  # This raises an exception if invalid
            serializer.save()
            return success_response(serializer.data)
            
        except Exception as err:
            return fail_response(error=err)
    
    def get(self, request):
        try:
            user = request.user
            
            orders = Order.objects.filter(sender = user)
            serializer = OrderSerializer(orders, many=True)

            return success_response(serializer.data)

        except Exception as err:
            return fail_response(error=err, status_code=500)

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
        
# class ShipmentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             serializer = ShipmentSerializer(data = request.data, context={'request':request})

#             if serializer.is_valid(raise_exception=True):
#                 serializer.save(sender = request.user)
#                 return success_response(serializer.data)
            
#         except Exception as err:
#             return fail_response(error=err)
        