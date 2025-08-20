#Factory for creating Billing objects
from billing.models import Billing

class BillingFactory:
    @staticmethod
    def create(owner_id, pet_id, appointment_id, service_id, notes=""):
        return {
            "owner_id": owner_id,
            "pet_id": pet_id,
            "appointment_id": appointment_id,
            "service_id": service_id,
            "amount": None,  # will auto-fill from ServiceCost in model save()
            "status": Billing._meta.get_field("status").default,
            "description": notes,
        }
