from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSerializer, ReceiverSerializer
from .models import Order
from utils.response import success_response, fail_response
# Create your views here.

class OrderView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data = request.data)
        serializer.is_valid()
        serializer.save()
        
        return Response({
            'message': 'Successfully',
            'data': serializer.data
        })
    
    def get(self, request):
        try:
            user = request.user
            
            orders = Order.objects.filter(sender = user)
            serializer = OrderSerializer(orders, many=True)

            return success_response(serializer.data)

        except Exception as err:
            return fail_response(error=err, status_code=500)
        
class ReceiverView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ReceiverSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Successfully",
            "data": serializer.data
        })
