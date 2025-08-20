from decimal import Decimal

def calculate_total(amount, discount_rate=0.0, tax_rate=0.15):
   
    if not amount:
        return Decimal('0.00')

    amount = Decimal(amount)
    discount_rate = Decimal(str(discount_rate))
    tax_rate = Decimal(str(tax_rate))

    total = amount * (Decimal('1.0') - discount_rate)  # discount
    total = total * (Decimal('1.0') + tax_rate)        # tax
    return total.quantize(Decimal('0.01'))  # round to 2 decimals
