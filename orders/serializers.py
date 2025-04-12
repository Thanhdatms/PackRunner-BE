from rest_framework import serializers
from .models import Order, Shipment
from utils.validate import generate_shipment_code

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['shipment_type', 'size', 'weight', 'note']

    # def validate_deliverer(self, value):
    #     ALLOWED_GROUPS = ['Employee']
    #     if not value.is_active:
    #         raise serializers.ValidationError("User is not active.")
        
    #     if not value.groups.filter(name__in=ALLOWED_GROUPS).exists():
    #         raise serializers.ValidationError("User is not authorized as a deliverer.")  
    #     return value
    
class OrderSerializer(serializers.ModelSerializer):
    shipment = ShipmentSerializer(write_only=True)  # Change to singular

    class Meta:
        model = Order
        fields = '__all__'
        managed = True
        read_only_fields = ['order_status', 'created', 'sender']

    def validate_total_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Please check the total price!')
        return value
    
    def create(self, validated_data): 
        shipment_data = validated_data.pop('shipment', None)
        request = self.context.get('request')
        order = Order.objects.create(sender=request.user, **validated_data)
        order.order_status = 'Ordered'
        shipment_code = generate_shipment_code(f"SHIP-{order.id}")

        if shipment_data:
            Shipment.objects.create(order=order, **shipment_data, shipment_code=shipment_code)
        return order    
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_status']   
