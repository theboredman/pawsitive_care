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
import json
from datetime import datetime

@login_required
def pet_list(request):
    """Enhanced pet listing with advanced search"""
    # Get base queryset
    if request.user.is_staff:
        pets = Pet.objects.active()
    else:
        pets = Pet.objects.active().by_owner(request.user)

    # Advanced search functionality
    search_query = request.GET.get('search', '').strip()
    species_filter = request.GET.get('species', '')
    sort_by = request.GET.get('sort', '-created_at')

    if search_query:
        pets = pets.search(search_query)
    if species_filter:
        pets = pets.by_species(species_filter)
    
    # Sorting
    valid_sort_fields = ['name', '-name', 'created_at', '-created_at', 'species', '-species']
    if sort_by in valid_sort_fields:
        pets = pets.order_by(sort_by)

    # Pagination with larger page size
    paginator = Paginator(pets, 12)  # Show 12 pets per page
    page = request.GET.get('page')
    pets = paginator.get_page(page)

    context = {
        'pets': pets,
        'search_query': search_query,
        'species_filter': species_filter,
        'sort_by': sort_by,
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
    """Enhanced pet creation with validation"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Process basic pet information
                pet_data = {
                    'name': request.POST.get('name'),
                    'species': request.POST.get('species'),
                    'breed': request.POST.get('breed', ''),
                    'gender': request.POST.get('gender'),
                    'owner': request.user,
                    'color': request.POST.get('color', ''),
                    'medical_conditions': request.POST.get('medical_conditions', ''),
                    'special_notes': request.POST.get('special_notes', ''),
                    'vaccination_status': request.POST.get('vaccination_status', 'UNKNOWN')
                }

                # Handle age field
                age = request.POST.get('age')
                if age:
                    try:
                        pet_data['age'] = int(age)
                        if pet_data['age'] < 0:
                            raise ValidationError('Age cannot be negative')
                    except ValueError:
                        raise ValidationError('Invalid age value')

                weight = request.POST.get('weight')
                if weight:
                    try:
                        pet_data['weight'] = float(weight)
                    except ValueError:
                        raise ValidationError('Invalid weight value')

                microchip_id = request.POST.get('microchip_id', '').strip()
                if microchip_id:
                    # Check if microchip ID is unique
                    if Pet.objects.filter(microchip_id=microchip_id).exists():
                        raise ValidationError('This microchip ID is already registered')
                    pet_data['microchip_id'] = microchip_id

                # Create the pet
                pet = Pet.objects.create(**pet_data)

                # Handle photo upload
                if 'pet_photo' in request.FILES:
                    try:
                        photo = PetPhoto(
                            pet=pet,
                            image=request.FILES['pet_photo'],
                            is_primary=True,
                            caption=request.POST.get('photo_caption', '')
                        )
                        photo.full_clean()  # Validate the photo
                        photo.save()
                    except ValidationError as e:
                        raise ValidationError(f'Invalid photo: {str(e)}')

                messages.success(request, f'{pet.name} has been registered successfully!')
                
                # Handle AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': f'{pet.name} has been registered successfully!',
                        'redirect_url': reverse('pets:pet_detail', kwargs={'pk': pet.pk})
                    })
                
                return redirect('pets:pet_detail', pk=pet.pk)

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating pet: {str(e)}')

    # GET request - show form
    context = {
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
    """Update pet information"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        try:
            # Update pet information
            pet.name = request.POST.get('name')
            pet.breed = request.POST.get('breed')
            pet.age = int(request.POST.get('age'))
            pet.gender = request.POST.get('gender')
            pet.weight = request.POST.get('weight')
            pet.color = request.POST.get('color')
            pet.microchip_id = request.POST.get('microchip_id')
            pet.medical_conditions = request.POST.get('medical_conditions')
            pet.special_notes = request.POST.get('special_notes')
            pet.vaccination_status = request.POST.get('vaccination_status', 'UNKNOWN')
            pet.save()

            messages.success(request, f'{pet.name}\'s information has been updated!')
            return redirect('pets:pet_detail', pk=pet.pk)
        except Exception as e:
            messages.error(request, f'Error updating pet: {str(e)}')

    return render(request, 'pets/pet_form.html', {
        'pet': pet,
        'species_choices': Pet.SPECIES_CHOICES,
        'gender_choices': Pet.GENDER_CHOICES
    })

@login_required
@require_POST
def add_medical_record(request, pk):
    """Enhanced medical record addition with validation"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff:
        raise PermissionDenied

    try:
        with transaction.atomic():
            # Validate and parse dates
            try:
                record_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                raise ValidationError('Invalid date format')

            next_visit = request.POST.get('next_visit_date')
            next_visit_date = None
            if next_visit:
                try:
                    next_visit_date = datetime.strptime(next_visit, '%Y-%m-%d').date()
                except ValueError:
                    raise ValidationError('Invalid next visit date format')

            # Create and validate record
            record = MedicalRecord(
                pet=pet,
                date=record_date,
                record_type=request.POST.get('record_type'),
                description=request.POST.get('description'),
                vet_notes=request.POST.get('vet_notes', ''),
                next_visit_date=next_visit_date
            )

            # Full validation
            record.full_clean()
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

    except ValidationError as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
    except Exception as e:
        messages.error(request, f'Error adding medical record: {str(e)}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return redirect('pets:pet_detail', pk=pk)

@login_required
@require_POST
def pet_photo_add(request, pk):
    """Add a photo to a pet"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied
    
    try:
        photo = PetPhoto.objects.create(
            pet=pet,
            image=request.FILES['image'],
            caption=request.POST.get('caption', ''),
            is_primary=request.POST.get('is_primary') == 'on'
        )
        messages.success(request, 'Photo uploaded successfully!')
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
    """Enhanced document upload with validation and organization"""
    pet = get_object_or_404(Pet.objects.active(), pk=pk)
    
    if not request.user.is_staff and pet.owner != request.user:
        raise PermissionDenied

    try:
        with transaction.atomic():
            # Validate file
            if 'file' not in request.FILES:
                raise ValidationError('No file was uploaded')

            file = request.FILES['file']
            
            # Validate file size
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError('File size cannot exceed 5MB')

            # Validate file type
            ext = file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
            if ext not in allowed_extensions:
                raise ValidationError(f'File type .{ext} is not supported')

            # Create document with sanitized filename
            document = PetDocument(
                pet=pet,
                document_type=request.POST.get('document_type'),
                file=file,
                title=request.POST.get('title'),
                description=request.POST.get('description', '')
            )

            # Full validation
            document.full_clean()
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

    except ValidationError as e:
        messages.error(request, str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)})
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
            # Get pet name before deletion for the success message
            pet_name = pet.name
            # Use the delete method we defined in the model
            # This will handle cleaning up all related files and data
            pet.delete()
            messages.success(request, f'{pet_name} has been deleted successfully!')
            return redirect('pets:pet_list')
        except Exception as e:
            messages.error(request, f'Error deleting pet: {str(e)}')
            return redirect('pets:pet_detail', pk=pk)

    return render(request, 'pets/pet_confirm_delete.html', {'pet': pet})