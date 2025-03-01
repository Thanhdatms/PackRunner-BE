from rest_framework import serializers
from .models import Receiver, Order

# Destination serializer

# class ReceiverSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Receiver
#         fields = []

# class ShipmentSerializer(serializers.ModelSerializer):
#     pass

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        managed = True

    def validate_total_price(self, attrs):
        if attrs < 0:
            raise serializers.ValidationError('Please check the total price!')
        return attrs
    
    
