from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('vet', 'Veterinarian'),
        ('staff', 'Staff'),
        ('client', 'Client'),
    ]
    
    phone = models.CharField(max_length=20, blank=False)
    address = models.TextField(blank=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_vet(self):
        return self.role == 'vet'
    
    def is_staff_member(self):
        return self.role == 'staff'
    
    def is_client(self):
        return self.role == 'client'
