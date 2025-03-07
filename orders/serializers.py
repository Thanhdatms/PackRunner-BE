from rest_framework import serializers
from .models import Order, Shipment

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        managed = True

    def validate_total_price(self, attrs):
        if attrs < 0:
            raise serializers.ValidationError('Please check the total price!')
        return attrs
    

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = '__all__'

    def validate_deliverer(self, value):
        ALLOWED_GROUPS = ['Employee']
        
        if not value.is_active:
            raise serializers.ValidationError("User is not active.")
        
        if not value.groups.filter(name__in=ALLOWED_GROUPS).exists():
            raise serializers.ValidationError("User is not authorized as a deliverer.")
        
        return value

