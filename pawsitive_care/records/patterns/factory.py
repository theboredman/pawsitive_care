from pets.models import Pet

class MedicalRecordFactory:
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
