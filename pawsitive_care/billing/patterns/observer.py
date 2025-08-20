#Observer Pattern Implementation for Billing Notifications
from django.core.mail import send_mail
from django.conf import settings
from billing.models import Billing as billing
class BillingObserver:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def notify(self, record):
        for callback in self.subscribers:
            callback(billing)

class EmailNotifier():
    def __call__(self, record):
        subject = f"Billing Notification - Invoice {billing.billing_id}"
        message = (
             f"""
        Hello {billing.owner.get_full_name()},
        
        Your invoice with ID {billing.billing_id} for pet {billing.pet.name} 
        is {billing.status}. Amount: ${billing.amount}

        Thank you!
        """
        )
        
        recipient_list = [billing.pet.owner.email]  # Send to pet owner
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)




class SMSNotifier():
    def update(self, billing):
        print(f"📱 SMS: Invoice {billing.billing_id} is {billing.status}")


class BillingSubject:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self, billing):
        for obs in self.observers:
            obs.update(billing)
