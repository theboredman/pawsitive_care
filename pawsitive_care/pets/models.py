from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import os

# Import patterns
from .patterns.repository import PetQuerySet
from .patterns.observer import PetObserver, EmailNotifier

class Pet(models.Model):
    """Base Pet Model"""
    SPECIES_CHOICES = [
        ('DOG', 'Dog'),
        ('CAT', 'Cat'),
        ('BIRD', 'Bird'),
        ('RABBIT', 'Rabbit'),
        ('HAMSTER', 'Hamster'),
        ('GUINEA_PIG', 'Guinea Pig'),
        ('FISH', 'Fish'),
        ('TURTLE', 'Turtle'),
        ('SNAKE', 'Snake'),
        ('LIZARD', 'Lizard'),
        ('FERRET', 'Ferret'),
        ('HORSE', 'Horse'),
        ('CHICKEN', 'Chicken'),
        ('PARROT', 'Parrot'),
        ('OTHER', 'Other'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(help_text="Age in years", null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=50, blank=True)
    microchip_id = models.CharField(max_length=50, blank=True, unique=True)
    
    # Owner information
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets')
    
    # Medical information
    medical_conditions = models.TextField(blank=True)
    special_notes = models.TextField(blank=True)
    vaccination_status = models.CharField(
        max_length=20,
        choices=[
            ('UP_TO_DATE', 'Up to Date'),
            ('DUE_SOON', 'Due Soon'),
            ('OVERDUE', 'Overdue'),
            ('UNKNOWN', 'Unknown')
        ],
        default='UNKNOWN',
        help_text="Current status of pet's vaccinations"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Repository Pattern implementation
    objects = PetQuerySet.as_manager()

    # Observer Pattern implementation
    observers = []

    @classmethod
    def register_observer(cls, observer):
        cls.observers.append(observer)

    @classmethod
    def notify_observers(cls, pet, action):
        for observer in cls.observers:
            observer.update(pet, action)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        self.notify_observers(self, 'created' if is_new else 'updated')

    def delete(self, *args, **kwargs):
        """Override delete to handle related files and data"""
        # Delete all associated photos and their files
        for photo in self.photos.all():
            if photo.image:
                # Delete the actual image file
                if os.path.isfile(photo.image.path):
                    os.remove(photo.image.path)
            photo.delete()

        # Delete all associated documents and their files
        for document in self.documents.all():
            if document.file:
                # Delete the actual document file
                if os.path.isfile(document.file.path):
                    os.remove(document.file.path)
            document.delete()

        # Delete all medical records
        self.medical_records.all().delete()

        # Notify observers before deletion
        self.notify_observers(self, 'deleted')

        # Call the parent class delete method
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['owner']),
            models.Index(fields=['species']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

    def display_age(self):
        """Returns a formatted string of the pet's age"""
        return f"{self.age} years old"

class MedicalRecord(models.Model):
    """Medical history tracking"""
    RECORD_TYPES = [
        ('CHECKUP', 'Regular Checkup'),
        ('VACCINE', 'Vaccination'),
        ('TREATMENT', 'Treatment'),
        ('SURGERY', 'Surgery'),
        ('TEST', 'Medical Test'),
        ('INJURY', 'Injury Care'),
        ('DENTAL', 'Dental Care'),
        ('EMERGENCY', 'Emergency Visit'),
        ('OTHER', 'Other'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateField()
    record_type = models.CharField(max_length=50, choices=RECORD_TYPES)
    description = models.TextField()
    vet_notes = models.TextField(blank=True)
    next_visit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.pet.name}'s {self.record_type} on {self.date}"

def pet_document_path(instance, filename):
    """Strategy Pattern: File upload path strategy"""
    ext = filename.split('.')[-1]
    return f'pet_documents/{instance.pet.id}/{instance.document_type}/{timezone.now().strftime("%Y%m%d-%H%M%S")}.{ext}'

class PetPhoto(models.Model):
    """Photo storage for pets"""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='pet_photos/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Photo of {self.pet.name}"
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set all other photos of this pet to non-primary
            PetPhoto.objects.filter(pet=self.pet, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

class PetDocument(models.Model):
    """Document storage for pets"""
    DOCUMENT_TYPES = [
        ('VACCINATION', 'Vaccination Record'),
        ('MEDICAL', 'Medical Report'),
        ('PRESCRIPTION', 'Prescription'),
        ('OTHER', 'Other Document'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=pet_document_path)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.pet.name}'s {self.get_document_type_display()}"

    def clean(self):
        if self.file:
            ext = self.file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            if ext not in allowed_extensions:
                raise ValidationError(f'File type .{ext} is not supported')
