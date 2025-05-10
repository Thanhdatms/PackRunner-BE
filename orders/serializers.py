from rest_framework import serializers
from .models import Order, Shipment, Payments
from utils.validate import generate_shipment_code

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['shipment_code','shipment_type', 'size', 'weight', 'note',
                  'receiver_name', 'receiver_address', 'receiver_province',
                  'receiver_district', 'receiver_ward', 'receiver_latitude',
                  'sender_name', 'sender_address', 'sender_province',
                  'sender_district', 'sender_ward', 'receiver_longitude',]
        read_only_fields = ['shipment_code']
class PaymentSerializer(serializers.ModelSerializer):
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Payments
        fields = [ 'amount', 'payment_method','payment_status', 'order']
        extra_kwargs = {
            'order': {'required': False}
        }

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
    payments = PaymentSerializer(many=True)
    shipments = ShipmentSerializer(many=True)
    class Meta:
        model = Order
        fields = [
            'id', 'total_price', 'order_status', 'created',
            'payments', 'shipments'
        ]
        read_only_fields = ['id', 'created', 'order_status', 'total_price']
        managed = True

    def validate_total_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Please check the total price!')
        return value

    def create(self, validated_data):
        shipments_data = validated_data.pop('shipments', []) 
        payments_data = validated_data.pop('payments', [])
        request = self.context.get('request')
        order = Order.objects.create(total_price = 100,sender=request.user, **validated_data)
        order.order_status = 'Ordered'
        shipment_code = generate_shipment_code(f"SHIP-{order.id}")

        if shipments_data:
            Shipment.objects.create(order=order, shipment_code=shipment_code, **shipments_data[0])
        if payments_data:
            Payments.objects.create(order=order, payment_status = Payments.PaymentStatus.PENDING,  **payments_data[0])
        return order
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_status']   

class OrderDetailSerializer(serializers.ModelSerializer):
    shipments = ShipmentSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'total_price', 'order_status','created',
            'shipments', 'payments'  # Updated field names
        ]

    def validate_total_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Please check the total price!')
        return value
    
class OrderStatisticsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_amount = serializers.FloatField()
    ordered_orders = serializers.IntegerField()
    in_transit_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
