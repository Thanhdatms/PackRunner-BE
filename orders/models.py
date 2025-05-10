from django.db import models
from django.utils.timezone import now
from users.models import User

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        ORDERED = 'Ordered'
        IN_TRANSIT = 'In Transit'
        DELIVERED = 'Delivered'

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2) 
    order_status = models.CharField(max_length=15, choices=OrderStatus.choices)

    created = models.DateTimeField(default=now, blank=True, null=True)

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
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    shipment_code = models.CharField(max_length=50, unique=True)
    deliverer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deliveries', null=True, blank=True)
    shipment_type = models.CharField(max_length=20, choices=ShipmentType.choices)  # Increased max_length
    size = models.CharField(max_length=10, choices=ShipmentSize.choices)
    weight = models.IntegerField()
    note = models.CharField(max_length=200, null=True, blank=True)

    receiver_name = models.CharField(max_length=100, null=False, blank=False)
    receiver_phone_number = models.CharField(max_length=15, null=True, blank=False)
    receiver_address = models.CharField(max_length=100, null=False, blank=False)
    receiver_province = models.CharField(max_length=100, null=False, blank=False)
    receiver_district = models.CharField(max_length=100, null=False, blank=False)
    receiver_ward = models.CharField(max_length=100, null=False, blank=False)
    receiver_latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    receiver_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    sender_name = models.CharField(max_length=100, null=False, blank=False)
    sender_phone_number = models.CharField(max_length=15, null=True, blank=False)
    sender_address = models.CharField(max_length=100, null=False, blank=False)
    sender_province = models.CharField(max_length=100, null=False, blank=False)
    sender_district = models.CharField(max_length=100, null=False, blank=False)
    sender_ward = models.CharField(max_length=100, null=False, blank=False)
    sender_latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    sender_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

class ShipmentTracking(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, to_field="shipment_code", db_column="shipment_code")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True) 
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    timestamp = models.DateTimeField(default=now, blank=True, null=True)

class Payments(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending'
        COMPLETED = 'Completed'
        FAILED = 'Failed'

    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=15, choices=PaymentStatus.choices)
    payment_method = models.CharField(max_length=50)  # e.g., Credit Card, PayPal
    created = models.DateTimeField(default=now, blank=True, null=True)

class Transaction(models.Model):
    class TransactionStatus(models.TextChoices):
        SUCCESS = 'Success'
        FAILURE = 'Failure'

    payment = models.ForeignKey(Payments, on_delete=models.CASCADE, related_name='transactions')
    transaction_status = models.CharField(max_length=15, choices=TransactionStatus.choices)
    created = models.DateTimeField(default=now, blank=True, null=True)