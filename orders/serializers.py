from rest_framework import serializers
from .models import Order, Shipment, Payments
from utils.validate import generate_shipment_code
import os
import requests

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['shipment_code','shipment_type', 'size', 'weight', 'note',
                  'receiver_name', 'receiver_phone_number','receiver_address', 'receiver_province',
                  'receiver_district', 'receiver_ward', 'receiver_longitude','receiver_latitude',
                  'sender_name','receiver_phone_number', 'sender_address', 'sender_province',
                  'sender_district', 'sender_ward', 'sender_longitude','sender_latitude',]
        read_only_fields = ['shipment_code']

class PaymentSerializer(serializers.ModelSerializer):
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Payments
        fields = [ 'amount', 'payment_method','payment_status', 'order']
        read_only_fields = ['payment_status', 'amount', 'order']
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

    def validate_total_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Please check the total price!')
        return value

    def create(self, validated_data):
        shipments_data = validated_data.pop('shipments', []) 
        payments_data = validated_data.pop('payments', [])
        request = self.context.get('request')
        
        order = Order.objects.create(
            total_price =self.calculate_total_price(shipments_data),
            sender=request.user, 
            **validated_data
            )
        order.order_status = 'Ordered'
        shipment_code = generate_shipment_code(f"SHIP-{order.id}")

        if shipments_data:
            Shipment.objects.create(order=order, shipment_code=shipment_code, **shipments_data[0])
        if payments_data:
            Payments.objects.create(order=order, payment_status = Payments.PaymentStatus.PENDING, amount = order.total_price,  **payments_data[0])
        return order
    
    def calculate_total_price(self, shipments_data):
        total_price = 0
        for shipment in shipments_data:
            weight = shipment.get('weight', 0)
            size = shipment.get('size', 'M')
            if size == 'S':
                total_price += weight * 10000
            elif size == 'M':
                total_price += weight * 20000
            elif size == 'L':
                total_price += weight * 30000
            elif size == 'XL':
                total_price += weight * 40000
            
        reciver_address = shipments_data[0].get('receiver_address', '')
        reciver_province = shipments_data[0].get('receiver_province', '')
        reciver_district = shipments_data[0].get('receiver_district', '')
        reciver_ward = shipments_data[0].get('receiver_ward', '')

        sender_address = shipments_data[0].get('sender_address', '')
        sender_province = shipments_data[0].get('sender_province', '')
        sender_district = shipments_data[0].get('sender_district', '')
        sender_ward = shipments_data[0].get('sender_ward', '')
        
        origin = f"{sender_address}, {sender_province}, {sender_district}, {sender_ward}"
        destination = f"{reciver_address}, {reciver_province}, {reciver_district}, {reciver_ward}"

        distance = self.calculate_distance(origin, destination)

        total_price += distance * 10000  # Assuming a rate of 10000 per km

        return total_price

    def calculate_distance(self, origin, destination):
        url_template = os.environ.get('GOOGLE_MAPS_ESTIMATE_URL')
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        url = url_template.format(destinations=destination, origins=origin, key=api_key)
        data = requests.get(url).json()

        distance_meters = data['rows'][0]['elements'][0]['distance']['value']
        return distance_meters / 1000  # Convert to kilometers 
        
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
