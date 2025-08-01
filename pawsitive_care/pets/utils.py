"""
Utility functions and helpers for the pets app
"""
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
import os
import uuid


def validate_file_size(file, max_size_mb=5):
    """
    Validate file size
    
    Args:
        file: The uploaded file
        max_size_mb: Maximum size in MB (default: 5)
        
    Raises:
        ValidationError: If file is too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB.')


def validate_file_extension(file, allowed_extensions):
    """
    Validate file extension
    
    Args:
        file: The uploaded file
        allowed_extensions: List of allowed extensions
        
    Raises:
        ValidationError: If file extension is not allowed
    """
    if hasattr(file, 'name') and file.name:
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                f'File type .{ext} is not supported. '
                f'Allowed types: {", ".join(allowed_extensions)}'
            )


def generate_unique_filename(filename):
    """
    Generate a unique filename while preserving the extension
    
    Args:
        filename: Original filename
        
    Returns:
        str: Unique filename
    """
    name, ext = os.path.splitext(filename)
    unique_name = f"{slugify(name)}_{uuid.uuid4().hex[:8]}{ext}"
    return unique_name


def get_pet_upload_path(instance, filename, subfolder=''):
    """
    Generate upload path for pet-related files
    
    Args:
        instance: Model instance
        filename: Original filename
        subfolder: Optional subfolder
        
    Returns:
        str: Upload path
    """
    pet_id = instance.pet.id if hasattr(instance, 'pet') else instance.id
    unique_filename = generate_unique_filename(filename)
    
    if subfolder:
        return f'pets/{pet_id}/{subfolder}/{unique_filename}'
    return f'pets/{pet_id}/{unique_filename}'


def format_pet_age(age):
    """
    Format pet age for display
    
    Args:
        age: Age in years
        
    Returns:
        str: Formatted age string
    """
    if age is None:
        return "Age unknown"
    elif age == 0:
        return "Less than 1 year old"
    elif age == 1:
        return "1 year old"
    else:
        return f"{age} years old"


def format_pet_weight(weight):
    """
    Format pet weight for display
    
    Args:
        weight: Weight in kg
        
    Returns:
        str: Formatted weight string
    """
    if weight is None:
        return "Weight not recorded"
    else:
        return f"{weight} kg"


def get_vaccination_status_class(status):
    """
    Get CSS class for vaccination status
    
    Args:
        status: Vaccination status
        
    Returns:
        str: CSS class name
    """
    status_classes = {
        'UP_TO_DATE': 'badge-success',
        'DUE_SOON': 'badge-warning',
        'OVERDUE': 'badge-danger',
        'UNKNOWN': 'badge-secondary'
    }
    return status_classes.get(status, 'badge-secondary')


def clean_microchip_id(microchip_id):
    """
    Clean and validate microchip ID
    
    Args:
        microchip_id: Raw microchip ID
        
    Returns:
        str: Cleaned microchip ID
        
    Raises:
        ValidationError: If microchip ID format is invalid
    """
    if not microchip_id:
        return ''
    
    # Remove whitespace and convert to uppercase
    cleaned = microchip_id.strip().upper()
    
    # Basic validation - microchip IDs should be alphanumeric
    if not cleaned.replace(' ', '').isalnum():
        raise ValidationError('Microchip ID should only contain letters and numbers.')
    
    # Length validation (typical microchip IDs are 10-15 characters)
    if len(cleaned.replace(' ', '')) < 10 or len(cleaned.replace(' ', '')) > 15:
        raise ValidationError('Microchip ID should be between 10 and 15 characters.')
    
    return cleaned


def get_allowed_file_extensions():
    """
    Get allowed file extensions for different file types
    
    Returns:
        dict: Dictionary of file type to allowed extensions
    """
    return {
        'documents': ['pdf', 'doc', 'docx', 'txt'],
        'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        'all_files': ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'bmp']
    }


def is_image_file(file):
    """
    Check if uploaded file is an image
    
    Args:
        file: Uploaded file
        
    Returns:
        bool: True if file is an image
    """
    if hasattr(file, 'content_type'):
        return file.content_type.startswith('image/')
    
    if hasattr(file, 'name'):
        ext = file.name.split('.')[-1].lower()
        return ext in get_allowed_file_extensions()['images']
    
    return False


def get_file_icon_class(filename):
    """
    Get Font Awesome icon class based on file extension
    
    Args:
        filename: Name of the file
        
    Returns:
        str: Font Awesome icon class
    """
    if not filename:
        return 'fas fa-file'
    
    ext = filename.split('.')[-1].lower()
    
    icon_map = {
        'pdf': 'fas fa-file-pdf',
        'doc': 'fas fa-file-word',
        'docx': 'fas fa-file-word',
        'txt': 'fas fa-file-alt',
        'jpg': 'fas fa-file-image',
        'jpeg': 'fas fa-file-image',
        'png': 'fas fa-file-image',
        'gif': 'fas fa-file-image',
        'bmp': 'fas fa-file-image',
    }
    
    return icon_map.get(ext, 'fas fa-file')


class PetQueryHelper:
    """Helper class for common pet queries"""
    
    @staticmethod
    def get_pets_needing_vaccination_update(user=None):
        """Get pets that might need vaccination updates"""
        from .models import Pet
        
        queryset = Pet.objects.filter(
            vaccination_status__in=['DUE_SOON', 'OVERDUE', 'UNKNOWN']
        )
        
        if user and not user.is_staff:
            queryset = queryset.filter(owner=user)
            
        return queryset
    
    @staticmethod
    def get_pets_with_upcoming_visits(user=None, days_ahead=30):
        """Get pets with upcoming medical visits"""
        from .models import MedicalRecord
        from django.utils import timezone
        from datetime import timedelta
        
        future_date = timezone.now().date() + timedelta(days=days_ahead)
        
        records = MedicalRecord.objects.filter(
            next_visit_date__lte=future_date,
            next_visit_date__gte=timezone.now().date()
        ).select_related('pet')
        
        if user and not user.is_staff:
            records = records.filter(pet__owner=user)
            
        return records
    
    @staticmethod
    def get_recent_medical_records(user=None, days_back=30):
        """Get recent medical records"""
        from .models import MedicalRecord
        from django.utils import timezone
        from datetime import timedelta
        
        past_date = timezone.now().date() - timedelta(days=days_back)
        
        records = MedicalRecord.objects.filter(
            date__gte=past_date
        ).select_related('pet').order_by('-date')
        
        if user and not user.is_staff:
            records = records.filter(pet__owner=user)
            
        return records
