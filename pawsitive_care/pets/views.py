from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from django.db import transaction
from django.core.files.storage import default_storage
from django.utils.text import slugify
from .models import Pet, MedicalRecord, PetDocument, PetPhoto
from .forms import PetForm, MedicalRecordForm, PetDocumentForm, PetPhotoForm, PetSearchForm
import json
from datetime import datetime
from .patterns.factory import MedicalRecordFactory, DocumentFactory, PhotoFactory
from .patterns.observer import EmailNotifier

# Initialize factories
medical_record_factory = MedicalRecordFactory()
document_factory = DocumentFactory()
photo_factory = PhotoFactory()

# Initialize observer
email_notifier = EmailNotifier()

@login_required
def pet_list(request):
    """Enhanced pet listing with advanced search using forms"""
    # Get base queryset
    if request.user.is_staff:
        pets = Pet.objects.active()
    else:
        pets = Pet.objects.active().for_user(request.user)

    # Use form for search handling
    search_form = PetSearchForm(request.GET)
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search', '').strip()
        species_filter = search_form.cleaned_data.get('species', '')
        sort_by = search_form.cleaned_data.get('sort_by', '-created_at')

        if search_query:
            pets = pets.search(search_query)
        if species_filter:
            pets = pets.by_species(species_filter)
        
        # Sorting with validation
        valid_sort_fields = ['name', '-name', 'created_at', '-created_at', 'species', '-species']
        if sort_by in valid_sort_fields:
            pets = pets.order_by(sort_by)

    # Pagination with larger page size
    paginator = Paginator(pets, 12)  # Show 12 pets per page
    page = request.GET.get('page')
    pets = paginator.get_page(page)

    context = {
        'pets': pets,
        'search_form': search_form,
        'species_choices': Pet.SPECIES_CHOICES,
    }

    # Handle AJAX requests for dynamic loading
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pet_list_html = render(request, 'pets/includes/pet_list_items.html', context).content.decode('utf-8')
        return JsonResponse({
            'html': pet_list_html,
            'has_next': pets.has_next(),
            'next_page': pets.next_page_number() if pets.has_next() else None
        })

    return render(request, 'pets/pet_list.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def pet_create(request):
    """Enhanced pet creation using forms"""
    if request.method == 'POST':
        form = PetForm(request.POST, user=request.user)
        photo_form = PetPhotoForm(request.POST, request.FILES)
        
        try:
            with transaction.atomic():
                if form.is_valid():
                    # Create the pet
                    pet = form.save(commit=False)
                    pet.owner = request.user
                    pet.save()

                    # Send confirmation email
                    subject = 'Pet Registration Confirmation - Pawsitive Care'
                    message = f"""Dear {request.user.get_full_name() or request.user.username},

Your pet has been successfully registered with Pawsitive Care!

Pet Details:
Name: {pet.name}
Species: {pet.get_species_display()}
Breed: {pet.breed}
Gender: {pet.get_gender_display()}
Age: {pet.age if pet.age else 'Not specified'} years
Weight: {pet.weight if pet.weight else 'Not specified'} kg
Microchip ID: {pet.microchip_id if pet.microchip_id else 'Not specified'}

Medical Conditions: {pet.medical_conditions if pet.medical_conditions else 'None'}

You can view and manage your pet's information anytime from your dashboard.

Thank you for choosing Pawsitive Care!"""

                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=True,
                    )

                    # Handle photo upload if provided
                    if 'image' in request.FILES:
                        if photo_form.is_valid():
                            # Delete any existing photos
                            PetPhoto.objects.filter(pet=pet).delete()
                            # Add new photo
                            photo = photo_form.save(commit=False)
                            photo.pet = pet
                            photo.is_primary = True
                            photo.save()
                        else:
                            for error in photo_form.errors.get('image', []):
                                messages.error(request, f'Photo error: {error}')

                    messages.success(request, f'{pet.name} has been registered successfully!')
                    
                    # Handle AJAX requests
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': f'{pet.name} has been registered successfully!',
                            'redirect_url': reverse('pets:pet_detail', kwargs={'pk': pet.pk})
                        })
                    
                    return redirect('pets:pet_detail', pk=pet.pk)
                else:
                    # Form validation failed
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')

        except Exception as e:
            messages.error(request, f'Error creating pet: {str(e)}')
    else:
        form = PetForm()
        photo_form = PetPhotoForm()

    # GET request - show form
    context = {
        'form': form,
        'photo_form': photo_form,
        'species_choices': Pet.SPECIES_CHOICES,
        'gender_choices': Pet.GENDER_CHOICES,
        'max_upload_size': 5 * 1024 * 1024,  # 5MB
        'allowed_extensions': ['jpg', 'jpeg', 'png'],
    }
    
    return render(request, 'pets/pet_form.html', context)

@login_required
def pet_detail(request, pk):
    """Enhanced pet detail view with organized information"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied
    
    # Get medical records with pagination
    page = request.GET.get('medical_page', 1)
    medical_records = pet.medical_records.all()
    medical_paginator = Paginator(medical_records, 5)
    medical_records_page = medical_paginator.get_page(page)

    # Get documents organized by type
    documents = {
        doc_type: pet.documents.filter(document_type=doc_type[0], is_active=True)
        for doc_type in PetDocument.DOCUMENT_TYPES
    }
    
    # Get photos with primary photo first
    photos = pet.photos.all()
    primary_photo = photos.filter(is_primary=True).first()
    other_photos = photos.filter(is_primary=False)

    # Get formatted age display
    age_display = pet.display_age()

    # Organize medical history by type
    medical_history = {}
    if medical_records.exists():
        medical_history = {
            record_type[0]: medical_records.filter(record_type=record_type[0])
            for record_type in MedicalRecord.RECORD_TYPES
        }

    context = {
        'pet': pet,
        'medical_records': medical_records_page,
        'documents': documents,
        'primary_photo': primary_photo,
        'other_photos': other_photos,
        'age': pet.age if pet.age is not None else None,
        'medical_history': medical_history,
        'document_types': PetDocument.DOCUMENT_TYPES,
        'record_types': MedicalRecord.RECORD_TYPES,
    }

    # Handle AJAX requests for dynamic loading
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.GET.get('load_section'):
            section = request.GET.get('load_section')
            template_name = f'pets/includes/{section}.html'
            html = render(request, template_name, context).content.decode('utf-8')
            return JsonResponse({'html': html})

    return render(request, 'pets/pet_detail.html', context)

@login_required
def pet_update(request, pk):
    """Update pet information using forms"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet, user=request.user)
        
        try:
            with transaction.atomic():
                if form.is_valid():
                    pet = form.save()
                    
                    # Send email notification for pet update
                    subject = 'Pet Information Updated - Pawsitive Care'
                    message = f"""Dear {request.user.get_full_name() or request.user.username},

Your pet's information has been successfully updated.

Updated Pet Details:
Name: {pet.name}
Species: {pet.get_species_display()}
Breed: {pet.breed}
Gender: {pet.get_gender_display()}
Age: {pet.age if pet.age else 'Not specified'} years
Weight: {pet.weight if pet.weight else 'Not specified'} kg
Color: {pet.color if pet.color else 'Not specified'}
Microchip ID: {pet.microchip_id if pet.microchip_id else 'Not specified'}

Medical Conditions: {pet.medical_conditions if pet.medical_conditions else 'None'}

You can view these updates anytime from your dashboard.

Thank you for choosing Pawsitive Care!"""

                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=True,
                    )

                    messages.success(request, f'{pet.name}\'s information has been updated!')
                    
                    # Handle AJAX requests
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': f'{pet.name}\'s information has been updated!',
                            'redirect_url': reverse('pets:pet_detail', kwargs={'pk': pet.pk})
                        })
                    
                    return redirect('pets:pet_detail', pk=pet.pk)
                else:
                    # Form validation failed
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')

        except Exception as e:
            messages.error(request, f'Error updating pet: {str(e)}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        form = PetForm(instance=pet, user=request.user)

    # GET request - show form with current values
    context = {
        'form': form,
        'pet': pet,
        'species_choices': Pet.SPECIES_CHOICES,
        'gender_choices': Pet.GENDER_CHOICES,
        'is_update': True,
    }
    return render(request, 'pets/pet_form.html', context)

@login_required
@require_POST
def add_medical_record(request, pk):
    """Enhanced medical record addition using forms"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff:
        raise PermissionDenied

    form = MedicalRecordForm(request.POST)
    
    try:
        with transaction.atomic():
            if form.is_valid():
                record = form.save(commit=False)
                record.pet = pet
                record.save()

                messages.success(request, 'Medical record added successfully!')
                
                # Return detailed JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'record': {
                            'id': record.id,
                            'date': record.date.strftime('%Y-%m-%d'),
                            'record_type': record.get_record_type_display(),
                            'description': record.description,
                            'next_visit_date': record.next_visit_date.strftime('%Y-%m-%d') if record.next_visit_date else None,
                            'html': render(request, 'pets/includes/medical_record.html', 
                                        {'record': record}).content.decode('utf-8')
                        }
                    })
                return redirect('pets:pet_detail', pk=pk)
            else:
                # Form validation failed
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f'{field}: {error}')
                
                error_message = '; '.join(error_messages)
                messages.error(request, error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': error_message})

    except Exception as e:
        messages.error(request, f'Error adding medical record: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return redirect('pets:pet_detail', pk=pk)

@login_required
@require_POST
def pet_photo_add(request, pk):
    """Add a photo to a pet using forms"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied
    
    form = PetPhotoForm(request.POST, request.FILES)
    
    try:
        if form.is_valid():
            with transaction.atomic():
                # Delete any existing photos
                PetPhoto.objects.filter(pet=pet).delete()
                # Add new photo
                photo = form.save(commit=False)
                photo.pet = pet
                photo.save()
                messages.success(request, 'Photo uploaded successfully!')
        else:
            # Form validation failed
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f'{field}: {error}')
            
            error_message = '; '.join(error_messages)
            messages.error(request, error_message)
    except Exception as e:
        messages.error(request, f'Error uploading photo: {str(e)}')
    
    return redirect('pets:pet_detail', pk=pk)

@login_required
@require_POST
def pet_photo_delete(request, photo_id):
    """Delete a pet's photo"""
    photo = get_object_or_404(PetPhoto, pk=photo_id)
    pet = photo.pet
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied
    
    try:
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting photo: {str(e)}')
    
    return redirect('pets:pet_detail', pk=pet.pk)

@login_required
@require_POST
def upload_document(request, pk):
    """Enhanced document upload using forms"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied

    form = PetDocumentForm(request.POST, request.FILES)

    try:
        with transaction.atomic():
            if form.is_valid():
                document = form.save(commit=False)
                document.pet = pet
                document.save()

                # Success response
                messages.success(request, 'Document uploaded successfully!')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'document': {
                            'id': document.id,
                            'url': document.file.url,
                            'title': document.title,
                            'type': document.get_document_type_display(),
                            'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    })
                return redirect('pets:pet_detail', pk=pk)
            else:
                # Form validation failed
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f'{field}: {error}')
                
                error_message = '; '.join(error_messages)
                messages.error(request, error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': error_message})

    except Exception as e:
        messages.error(request, f'Error uploading document: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})

    return redirect('pets:pet_detail', pk=pk)

@login_required
def search_pets(request):
    """AJAX search endpoint"""
    query = request.GET.get('q', '')
    pets = Pet.objects.search(query)[:10]  # Limit to 10 results
    
    results = [{
        'id': pet.id,
        'name': pet.name,
        'species': pet.get_species_display(),
        'breed': pet.breed,
        'owner': pet.owner.get_full_name(),
        'url': reverse('pets:pet_detail', args=[pet.id])
    } for pet in pets]
    
    return JsonResponse({'results': results})

@login_required
@require_POST
def edit_medical_record(request, record_id):
    """Edit an existing medical record"""
    record = get_object_or_404(MedicalRecord, pk=record_id)
    pet = record.pet
    
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        record.date = request.POST.get('date')
        record.record_type = request.POST.get('record_type')
        record.description = request.POST.get('description')
        record.vet_notes = request.POST.get('vet_notes', '')
        record.next_visit_date = request.POST.get('next_visit_date') or None
        record.save()
        
        messages.success(request, 'Medical record updated successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'record': {
                    'id': record.id,
                    'date': record.date.strftime('%Y-%m-%d'),
                    'record_type': record.record_type,
                    'description': record.description,
                    'next_visit_date': record.next_visit_date.strftime('%Y-%m-%d') if record.next_visit_date else None
                }
            })
    except Exception as e:
        messages.error(request, f'Error updating medical record: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return redirect('pets:pet_detail', pk=pet.pk)

@login_required
@require_POST
def delete_medical_record(request, record_id):
    """Delete a medical record"""
    record = get_object_or_404(MedicalRecord, pk=record_id)
    pet = record.pet
    
    if not request.user.is_staff:
        raise PermissionDenied
    
    try:
        record.delete()
        messages.success(request, 'Medical record deleted successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
    except Exception as e:
        messages.error(request, f'Error deleting medical record: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return redirect('pets:pet_detail', pk=pet.pk)

@login_required
@require_POST
def delete_document(request, document_id):
    """Delete a pet document"""
    document = get_object_or_404(PetDocument, pk=document_id)
    
    if not request.user.is_staff and document.pet.owner != request.user:
        raise PermissionDenied
    
    try:
        document.is_active = False
        document.save()
        messages.success(request, 'Document deleted successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
    except Exception as e:
        messages.error(request, f'Error deleting document: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return redirect('pets:pet_detail', pk=document.pet.pk)

@login_required
def pet_delete(request, pk):
    """Delete a pet"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        try:
            # Get pet details before deletion for the email
            pet_name = pet.name
            pet_species = pet.get_species_display()
            
            # Send email notification for pet deletion
            subject = 'Pet Removed - Pawsitive Care'
            message = f"""Dear {request.user.get_full_name() or request.user.username},

This email confirms that {pet_name} ({pet_species}) has been successfully removed from your Pawsitive Care profile.

If this was done by mistake, please contact our support team immediately.

Thank you for using Pawsitive Care!"""

            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
            
            # Use the delete method we defined in the model
            # This will handle cleaning up all related files and data
            pet.delete()
            messages.success(request, f'{pet_name} has been deleted successfully!')
            return redirect('pets:pet_list')
        except Exception as e:
            messages.error(request, f'Error deleting pet: {str(e)}')
            return redirect('pets:pet_detail', pk=pk)

    return render(request, 'pets/pet_confirm_delete.html', {'pet': pet})