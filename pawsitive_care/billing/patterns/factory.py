from billing.models import Billing


class BillingFactory:
    @staticmethod
    def create(owner_id, pet_id, appointment_id, amount, notes=""):
        return {
            "owner_id": owner_id,
            "pet_id": pet_id,
            "appointment_id": appointment_id,
            "total_amount": amount,
            "pay_status": Billing.PaymentStatus.PENDING,
            "notes": notes,
        }
