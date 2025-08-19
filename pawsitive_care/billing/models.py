# billing/models.py
from django.db import models
from django.conf import settings
from appointments.models import Appointment
from pets.models import Pet
from django.utils import timezone
class Billing(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    billing_id = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='billing')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='billings')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, help_text="Details of charges, treatments, medications, etc.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
            models.Index(fields=['pet']),
        ]

    def __str__(self):
        return f"Bill #{self.billing_id} - {self.pet.name} - {self.status}"

    def mark_as_paid(self):
        self.status = 'paid'
        self.paid_at = models.DateTimeField(auto_now=True)
        self.save()
