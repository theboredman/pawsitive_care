class Observer:
    def update(self, billing): pass


class EmailNotifier(Observer):
    def update(self, billing):
        print(f"📧 Email: Invoice {billing.billing_id} is {billing.pay_status}")


class SMSNotifier(Observer):
    def update(self, billing):
        print(f"📱 SMS: Invoice {billing.billing_id} is {billing.pay_status}")


class BillingSubject:
    def __init__(self):
        self.observers = []

    def attach(self, observer): 
        self.observers.append(observer)

    def notify(self, billing):
        for obs in self.observers:
            obs.update(billing)
