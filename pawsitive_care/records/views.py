from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pets.models import Pet
from .models import PetsMedicalRecord
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from .patterns.factory import NewMedicalRecordFactory,SurgeryRecordFactory
from .patterns.repository import MedicalRecordRepository,SurgeryRepository,SurgeryRecord
from .patterns.observer import RecordObserver,EmailNotificationObserver
from .form import PetsMedicalRecordForm
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse


User = get_user_model()

repository = MedicalRecordRepository()
factory = NewMedicalRecordFactory()
record_observer = RecordObserver()
record_observer.subscribe(EmailNotificationObserver())

@login_required
def add_medical_record(request):
    if request.method == 'POST':
        try:
            record_data = factory.create(request.POST, request.user)
            record = repository.create_record(record_data)
            record_observer.notify(record)

            return redirect(f"{reverse('records:add_medical_record')}?success=1&record_id={record.record_id}")

        except Pet.DoesNotExist:
            messages.error(request, "Selected pet does not exist.")
        except Exception as e:
            messages.error(request, f"Error adding record: {str(e)}")

    return render(request, 'Medical/add_medicalrecord.html', {
        'success': request.GET.get('success') == '1',
        'record_id': request.GET.get('record_id'),
        'pets': Pet.objects.all(),
        'user': request.user
    })

def view_records(request):
    query = request.GET.get('query')
    records = PetsMedicalRecord.objects.all()

    if query:
        # Try matching both pet ID and phone number
        records = records.filter(
            Q(pet__id__iexact=query) |
            Q(pet__owner__phone__icontains=query)
        )

    context = {
        'records': records,
        'title': 'All Medical Records',
    }
    return render(request, 'Medical/view_records.html', context)


@login_required
def my_pet_records(request):
    records = repository.get_records_by_owner(request.user)
    return render(request, 'Medical/my_pet_records.html', {
        'records': records,
        'title': 'My Pet Records'
    })




#record detail

@login_required
def record_detail(request, record_id):
    record = get_object_or_404(PetsMedicalRecord, pk=record_id)

    # Get primary photo or None
    primary_photo = record.pet.photos.filter(is_primary=True).first()

    user = request.user
    is_veterian = record.vaterian == user
    is_staff = user.is_staff
    is_client = not is_veterian and not is_staff  # Assuming clients are neither staff nor veterinarians

    context = {
        'record': record,
        'primary_photo': primary_photo,
        'title': 'Record Details',
        'is_veterian': is_veterian,
        'is_staff': is_staff,
        'is_client': is_client,
        'now': timezone.now(),
    }
    return render(request, 'Medical/record_detail.html', context)

@login_required
def update_record(request, record_id):
    record = get_object_or_404(PetsMedicalRecord, record_id=record_id)

    if record.vaterian != request.user:
        return HttpResponseForbidden("You are not allowed to edit this record.")

    if request.method == 'POST':
        form = PetsMedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('records:record_detail', record_id=record.record_id)  # Use record.record_id here
    else:
        form = PetsMedicalRecordForm(instance=record)

    return render(request, 'Medical/update_record.html', {'form': form, 'record': record})


@login_required
def delete_record(request, record_id):
    record = get_object_or_404(PetsMedicalRecord, record_id=record_id)

    if request.user != record.vaterian and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to delete this record.")

    if request.method == 'POST':
        record.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('records:view_records')

    return render(request, 'Medical/confirm_delete.html', {'record': record})


#surgery


surgery_factory = SurgeryRecordFactory()
surgery_repository = SurgeryRepository()
surgery_observer = RecordObserver()
surgery_observer.subscribe(EmailNotificationObserver())

@login_required
def add_surgery(request):
    if request.method == 'POST':
        try:
            surgery_data = surgery_factory.create(request.POST, request.user)
            surgery_record = surgery_repository.create_record(surgery_data)
            surgery_observer.notify(surgery_record)
            messages.success(request, f"Surgery record added for {surgery_record.pet.name}!")
            return redirect(f"{reverse('records:add_surgery')}?success=1&record_id={surgery_record.id}")

        except Pet.DoesNotExist:
            messages.error(request, "Selected pet does not exist.")
        except Exception as e:
            messages.error(request, f"Error adding surgery record: {str(e)}")

    return render(request, 'surgery/add_surgery.html', {
        'success': request.GET.get('success') == '1',
        'record_id': request.GET.get('record_id'),
        'pets': Pet.objects.all(),
        'user': request.user
    })


@login_required
def view_surgeries(request):
    query = request.GET.get('query', '').strip()
    surgeries = surgery_repository.get_all_records()

    if query:
        surgeries = [
            s for s in surgeries
            if query.lower() in s.pet.name.lower() or query in s.pet.owner.phone
        ]

    return render(request, 'surgery/view_records.html', {
        'surgeries': surgeries,
        'query': query,
        'title': 'All Surgery Records'
    })


@login_required
def surgery_detail(request, record_id):
    record = get_object_or_404(SurgeryRecord, pk=record_id)
    primary_photo = record.pet.photos.filter(is_primary=True).first()

    context = {
        'record': record,
        'primary_photo': primary_photo,
        'title': 'Surgery Details',
        'is_veterian': record.veterinarian == request.user,
        'is_staff': request.user.is_staff,
    }
    return render(request, 'surgery/surgery_detail.html', context)



#Define which record to add
@login_required
def add_record(request):
    """
    View to choose whether to add a Medical Record or Surgery Record.
    """
    if request.method == 'POST':
        record_type = request.POST.get('record_type')

        if record_type == 'medical':
            return redirect(reverse('records:add_medical_record'))
        elif record_type == 'surgery':
            return redirect(reverse('records:add_surgery'))
        else:
            messages.error(request, "Please select a valid record type.")

    return render(request, 'add_record.html', {
        'user': request.user
    })
