from django.contrib import admin
from .models import PetsMedicalRecord

@admin.register(PetsMedicalRecord)
class PetsMedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        'record_id',  # Use your actual primary key field name here
        'pet',
        'vaterian',
        'visit_date',
        'diagnosis',
        'treatment',
        'prescription',
        'vaccination_date',
        'created_at',
    )
    list_filter = ('visit_date', 'vaterian', 'pet')
    search_fields = ('pet__name', 'vaterian__username', 'diagnosis', 'treatment')
    ordering = ('-created_at',)
