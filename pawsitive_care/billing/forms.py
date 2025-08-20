# billing/forms.py
from django import forms
from .models import ServiceCost
from appointments.models import Appointment

class ServiceCostForm(forms.ModelForm):
    # Use Appointment.APPOINTMENT_TYPES for dropdown
    service_type = forms.ChoiceField(
        choices=Appointment.APPOINTMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'})
    )

    class Meta:
        model = ServiceCost
        fields = ['service_type', 'cost']
