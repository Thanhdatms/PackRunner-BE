from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.conf import settings
from django.utils.timezone import now, timedelta
import random


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    is_banned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Default to False until OTP is verified
    date_of_birth = models.DateField(blank=True, null=True) 
    created = models.DateTimeField(default=datetime.now, blank=True)
    
    otp = models.CharField(max_length=4, null=True)  # OTP code
    otp_expiry = models.DateTimeField(blank=True, null=True)  # Time for OTP expiry
    max_otp_try = models.IntegerField(default=settings.MAX_OTP_TRY)  # Number of attempts allowed for OTP
    otp_max_out = models.DateTimeField(blank=True, null=True)  # Lock out time after max failed attempts
    otp_require = models.BooleanField(default=True)  # Whether OTP is required

    username = None  # Disable username field
    is_staff = None
    last_login = None
    is_superuser = None
    date_joined = None

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def generate_otp(self):
        self.otp = str(random.randint(1000, 9999))
        self.otp_expiry = now() + timedelta(minutes=2)
        self.max_otp_try = settings.MAX_OTP_TRY  # Max attempts reset on OTP generation
        self.save()
        return self.otp

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Changed `user_id` to `user`
    address_line = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    street_name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)  
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)  
    is_default = models.BooleanField(default=False)