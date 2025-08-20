from pets.models import Pet
from records.models import PetsMedicalRecord
# Abstract Creator
class MedicalRecordCreator:
    def create(self, form_data, user):
        raise NotImplementedError


# Concrete Creator 1 — new record
class NewMedicalRecordFactory:
    def create(self, form_data, user):
        pet = Pet.objects.get(id=form_data.get('pet'))
        return {
            'pet': pet,
            'vaterian': user,
            'visit_date': form_data.get('visit_date'),
            'treatment': form_data.get('treatment'),
            'prescription': form_data.get('prescription'),
            'vaccination_date': form_data.get('vaccination_date'),
            'diagnosis': form_data.get('diagnosis'),
            'notes': form_data.get('notes'),
            'created_at': form_data.get('created_at'),
        }


class SurgeryRecordFactory:
    def create(self, form_data, user):
        pet = Pet.objects.get(id=form_data.get('pet'))
        return {
            'pet': pet,
            'veterinarian': user,
            'surgery_date': form_data.get('surgery_date'),
            'surgeon': form_data.get('surgeon'),
            'surgery_type': form_data.get('surgery_type'),
            'anesthesia_used': form_data.get('anesthesia_used'),
            'notes': form_data.get('notes'),
            'created_at': form_data.get('created_at'),
        }


FACTORY_REGISTRY = {
    "new": NewMedicalRecordFactory(),
    "surgery": SurgeryRecordFactory()
}


def get_factory(mode: str) -> MedicalRecordCreator:
    factory = FACTORY_REGISTRY.get(mode)
    if not factory:
        raise ValueError(f"Unknown record creation mode: {mode}")
    return factory
