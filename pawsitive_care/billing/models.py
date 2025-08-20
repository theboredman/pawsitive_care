# billing/models.py
from django.db import models
from django.conf import settings
from appointments.models import Appointment
from pets.models import Pet
from django.utils import timezone

# --- Service model ---
class ServiceCost(models.Model):
    SERVICE_CHOICES = [
        ('GENERAL', 'General Checkup'),
        ('VACCINATION', 'Vaccination'),
        ('SURGERY', 'Surgery'),
        ('ILLNESS', 'Illness / Injury'),
        ('FOLLOWUP', 'Follow-up'),
        ('OTHER', 'Others'),
    ]

    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, unique=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_service_type_display()} - ${self.cost}"


# --- Billing model ---
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
    service = models.ForeignKey(
        ServiceCost, on_delete=models.CASCADE, related_name='billings',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
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

    # --- Override save to calculate amount automatically ---
    def save(self, *args, **kwargs):
        if not self.amount and self.service:
            self.amount = self.service.cost
        super().save(*args, **kwargs)

    # --- Mark as paid ---
    def mark_as_paid(self):
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()

    # --- Calculate final amount with tax and discount ---
    def calculate_total(self, discount_rate=0.0, tax_rate=0.15):
        """
        Calculate the final amount after applying tax and user-defined discount.
        discount_rate: 0.10 = 10%
        tax_rate: 0.15 = 15%
        """
        if not self.amount:
            return 0.0

        total = self.amount
        total = total * (1 - discount_rate)  # apply discount first
        total = total * (1 + tax_rate)       # apply tax
        return round(total, 2)
