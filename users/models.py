from enum import unique
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .user_manager.custom_manager import CustomUserManager
from django.db import models
from django.db import models
from django.core.exceptions import ValidationError
import uuid


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as primary key
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False, max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True, auto_now_add=False, blank=True, null=True)
    genders = [
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE'),
    ]
    gender = models.CharField(max_length=30, choices=genders, null=True, blank=True)
    
    USERNAME_FIELD = 'username'
    objects = CustomUserManager()

    class Meta:
        db_table = 'tb_users'
        default_permissions = ()
        
    def clean(self):
        # Validate gender if it's set and not one of the allowed choices
        if self.gender not in dict(self.genders):
            raise ValidationError(f"Invalid gender: {self.gender}. Must be one of: {dict(self.genders)}.")
        super().clean()  # Call the parent class's clean method

    def __str__(self):
        return self.email