#Decorator Pattern Implementation for Billing
class Invoice:
    def __init__(self, amount):
        self.amount = amount

    def get_total(self):
        return self.amount


class InvoiceDecorator:
    def __init__(self, invoice):
        self.invoice = invoice

    def get_total(self):
        return self.invoice.get_total()


class TaxDecorator(InvoiceDecorator):
    def get_total(self):
        return self.invoice.get_total() * 1.10  # 10% tax


class DiscountDecorator(InvoiceDecorator):
    def get_total(self):
        return self.invoice.get_total() * 0.90  # 10% discount
