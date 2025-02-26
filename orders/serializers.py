from rest_framework import serializers
from .models import Payment, Destination, Shipment, Order

# Destination serializer

class DestinationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Destination
        fields = ['id', 'address_line', 'city', 'district', 'street_name']


class OrderSerializer(serializers.ModelSerializer):
    pass

class ShipmentSerializer(serializers.ModelSerializer):
    pass