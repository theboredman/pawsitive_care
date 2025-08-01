from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from .models import Pet, MedicalRecord, PetDocument, PetPhoto
import os


class PetForm(forms.ModelForm):
    """Form for creating and updating pets with comprehensive validation"""
    
    class Meta:
        model = Pet
        fields = [
            'name', 'species', 'breed', 'age', 'gender', 'weight', 
            'color', 'microchip_id', 'medical_conditions', 
            'special_notes', 'vaccination_status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pet name',
                'required': True
            }),
            'species': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'breed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter breed (optional)'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age in years',
                'min': 0,
                'max': 50
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'min': 0,
                'max': 1000,
                'step': 0.1
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pet color (optional)'
            }),
            'microchip_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Microchip ID (optional)'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any known medical conditions'
            }),
            'special_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special notes about the pet'
            }),
            'vaccination_status': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and age < 0:
            raise ValidationError('Age cannot be negative.')
        if age is not None and age > 50:
            raise ValidationError('Age seems unrealistic. Please verify.')
        return age

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and weight <= 0:
            raise ValidationError('Weight must be greater than 0.')
        if weight is not None and weight > 1000:
            raise ValidationError('Weight seems unrealistic. Please verify.')
        return weight

    def clean_microchip_id(self):
        microchip_id = self.cleaned_data.get('microchip_id')
        if microchip_id:
            microchip_id = microchip_id.strip()
            # Check uniqueness, excluding current instance if updating
            queryset = Pet.objects.filter(microchip_id=microchip_id)
            if self.instance_pk:
                queryset = queryset.exclude(pk=self.instance_pk)
            
            if queryset.exists():
                raise ValidationError('This microchip ID is already registered.')
        return microchip_id

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError('Pet name must be at least 2 characters long.')
        return name


class MedicalRecordForm(forms.ModelForm):
    """Form for adding medical records"""
    
    class Meta:
        model = MedicalRecord
        fields = ['date', 'record_type', 'description', 'vet_notes', 'next_visit_date']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'record_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the medical procedure or visit',
                'required': True
            }),
            'vet_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Veterinarian notes (optional)'
            }),
            'next_visit_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            from django.utils import timezone
            if date > timezone.now().date():
                raise ValidationError('Medical record date cannot be in the future.')
        return date

    def clean_next_visit_date(self):
        next_visit_date = self.cleaned_data.get('next_visit_date')
        record_date = self.cleaned_data.get('date')
        
        if next_visit_date and record_date:
            if next_visit_date <= record_date:
                raise ValidationError('Next visit date must be after the record date.')
        return next_visit_date


class PetDocumentForm(forms.ModelForm):
    """Form for uploading pet documents"""
    
    class Meta:
        model = PetDocument
        fields = ['document_type', 'title', 'description', 'file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Document description (optional)'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
                'required': True
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 5MB.')
            
            # Check file extension
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'File type .{ext} is not supported. '
                    f'Allowed types: {", ".join(allowed_extensions)}'
                )
        return file

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise ValidationError('Title must be at least 3 characters long.')
        return title


class PetPhotoForm(forms.ModelForm):
    """Form for uploading pet photos"""
    
    class Meta:
        model = PetPhoto
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Photo caption (optional)'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image size cannot exceed 5MB.')
            
            # Check if it's actually an image
            if not image.content_type.startswith('image/'):
                raise ValidationError('Please upload a valid image file.')
            
            # Check file extension
            ext = image.name.split('.')[-1].lower()
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'Image type .{ext} is not supported. '
                    f'Allowed types: {", ".join(allowed_extensions)}'
                )
        return image


class PetSearchForm(forms.Form):
    """Form for searching pets"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, breed, owner...',
            'autocomplete': 'off'
        })
    )
    species = forms.ChoiceField(
        required=False,
        choices=[('', 'All Species')] + Pet.SPECIES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('species', 'Species A-Z'),
            ('-species', 'Species Z-A'),
        ],
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
