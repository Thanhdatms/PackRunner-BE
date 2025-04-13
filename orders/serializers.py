from rest_framework import serializers
from .models import Order, Shipment, Payments
from utils.validate import generate_shipment_code

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['shipment_type', 'size', 'weight', 'note']

class PaymentSerializer(serializers.ModelSerializer):
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Payments
        fields = [ 'amount', 'payment_method','payment_status', 'order']

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('Please check the amount!')
        return value
    
    def create(self, validated_data): 
        request = self.context.get('request')
        payment = Payments.objects.create(**validated_data)
        payment.payment_status = 'Pending'
        payment.save()
        return payment
    
class OrderSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)  # Use the PaymentSerializer here
    class Meta:
        model = Order
        fields = [
            'id', 'total_price', 'order_status',
            'receiver_name', 'address', 'province', 'district', 'ward',
            'latitude', 'longitude', 'created',
            'payments'
        ]
        managed = True

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
