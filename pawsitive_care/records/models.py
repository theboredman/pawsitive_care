from django.db import models
from pets import models as pet_models
from django.conf import settings


class PetsMedicalRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    pet = models.ForeignKey(pet_models.Pet, on_delete=models.CASCADE,related_name='pets_medical_records')
    vaterian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets_medical_records_vaterian')
    visit_date = models.DateField()
    treatment = models.CharField(max_length=100)
    prescription = models.DateField()
    vaccination_date = models.DateField()
    diagnosis = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
           return f"{self.pet.name} - {self.vaterian.username} ({self.visit_date})"
    
class SurgeryRecord(models.Model):
    pet = models.ForeignKey(pet_models.Pet, on_delete=models.CASCADE,related_name='pets_surgery_records')
    veterinarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets_surgery_records_vaterian')
    surgeon = models.CharField(max_length=100,null= True, blank=True)
    surgery_date = models.DateField()
    surgery_type = models.CharField(max_length=255)
    anesthesia_used = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-surgery_date']
        verbose_name = 'Surgery Record'
        verbose_name_plural = 'Surgery Records'

    def __str__(self):
        return f"{self.pet.name} - {self.surgery_type} on {self.surgery_date}"
    
# Create your models here.
