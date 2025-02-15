from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20,  unique=True)
    is_banned =  models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_of_birth = models.DateTimeField(blank=False, default=datetime.now)
    created = models.DateTimeField(default=datetime.now, blank=True)

    username = None # loai bo truong user name trong abstract user
    is_staff = None
    last_login = None
    is_superuser = None
    date_joined = None
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []