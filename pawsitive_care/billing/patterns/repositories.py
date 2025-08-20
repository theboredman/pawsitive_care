#repository
from billing.models import Billing


class BillingRepository:
    @staticmethod
    def create_billing(**kwargs):
        return Billing.objects.create(**kwargs)

    @staticmethod
    def get_billing_by_id(billing_id):
        return Billing.objects.filter(billing_id=billing_id).first()

    @staticmethod
    def update_status(billing_id, status, payment_date=None):
        billing = BillingRepository.get_billing_by_id(billing_id)
        if billing:
            billing.status = status
            if payment_date:
                billing.paid_at = payment_date
            billing.save()
        return billing
