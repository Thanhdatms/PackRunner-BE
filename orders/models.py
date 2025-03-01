from django.db import models
from django.utils.timezone import now
from users.models import User

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        ORDERED = 'Ordered'
        IN_TRANSIT = 'In Transit'
        DELIVERED = 'Delivered'

    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2) 
    order_status = models.CharField(max_length=15, choices=OrderStatus.choices)
    created = models.DateTimeField(default=now, blank=True, null=True)

class Receiver(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)

    address = models.CharField(max_length=100, null=False, blank=False)
    province = models.CharField(max_length=100, null=False, blank=False)
    district = models.CharField(max_length=100, null=False, blank=False)
    ward = models.CharField(max_length=100, null=False, blank=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)  
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)  

class Shipment(models.Model):
    class ShipmentType(models.TextChoices):
        FOOD = 'Food'
        CLOTH = 'Cloth'
        ELECTRONIC = 'Electronic'

    class ShipmentSize(models.TextChoices):
        S = 'Small'
        M = 'Medium'
        L = 'Large'
        XL = 'X-large'
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipment_code = models.CharField(max_length=50, unique=True)  # Ensure it is unique
    deliverer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shipments')
    shipment_type = models.CharField(max_length=20, choices=ShipmentType.choices)  # Increased max_length
    size = models.CharField(max_length=10, choices=ShipmentSize.choices)
    weight = models.IntegerField()
    note = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField(default=now, blank=True, null=True)

class ShipmentTracking(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, to_field="shipment_code", db_column="shipment_code")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True) 
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    timestamp = models.DateTimeField(default=now, blank=True, null=True)
