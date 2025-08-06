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
    
# Create your models here.
