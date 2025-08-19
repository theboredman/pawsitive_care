from .repositories import BillingRepository
from .factory import BillingFactory


class BillingFacade:
    def __init__(self, strategy, subject):
        self.strategy = strategy
        self.subject = subject

    def process_invoice(self, owner_id, pet_id, appointment_id, amount, notes=""):
        # 1. Create invoice (Factory)
        invoice_data = BillingFactory.create(owner_id, pet_id, appointment_id, amount, notes)
        billing = BillingRepository.create_billing(**invoice_data)

        # 2. Process payment (Strategy)
        result = self.strategy.pay(billing.total_amount)
        billing.pay_status = "PAID"
        billing.save()

        # 3. Notify observers (Observer)
        self.subject.notify(billing)

        return billing, result
