from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pets.models import Pet
from .models import PetsMedicalRecord
from django.contrib.auth import get_user_model

from .patterns.factory import MedicalRecordFactory
from .patterns.repository import MedicalRecordRepository
from .patterns.observer import RecordObserver

User = get_user_model()

repository = MedicalRecordRepository()
factory = MedicalRecordFactory()
observer = RecordObserver()

@login_required
def add_record(request):
    if request.method == 'POST':
        try:
            record_data = factory.create(request.POST, request.user)
            record = repository.create_record(record_data)
            observer.notify(record)

            return render(request, 'add_record.html', {
                'success': True,
                'pets': Pet.objects.all(),
                'user': request.user
            })

        except Pet.DoesNotExist:
            messages.error(request, "Selected pet does not exist.")
        except Exception as e:
            messages.error(request, f"Error adding record: {str(e)}")

    return render(request, 'add_record.html', {
        'pets': Pet.objects.all(),
        'user': request.user
    })

@login_required
def view_records(request):
    pet_id = request.GET.get('pet_id')
    if pet_id:
        records = PetsMedicalRecord.objects.filter(pet__id=pet_id)
    else:
        records = PetsMedicalRecord.objects.all()

    context = {
        'records': records,
        'title': 'All Medical Records',
    }
    return render(request, 'view_records.html', context)


@login_required
def my_pet_records(request):
    records = repository.get_records_by_owner(request.user)
    return render(request, 'my_pet_records.html', {
        'records': records,
        'title': 'My Pet Records'
    })

@login_required
def record_detail(request, record_id):
    record = get_object_or_404(PetsMedicalRecord, id=record_id, pet__owner=request.user)
    return render(request, 'record_detail.html', {
        'record': record,
        'title': 'Record Details'
    })
