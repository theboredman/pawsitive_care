#strategy.py
from abc import ABC, abstractmethod
import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages


stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, request, amount):
        pass


class StripePayment(PaymentStrategy):
    def pay(self, request, amount):
        # amount in cents
        amount_cents = int(amount * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Pet Bill Payment',
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/billing/success/'),
            cancel_url=request.build_absolute_uri('/billing/cancel/'),
        )
        return redirect(session.url)



class PaypalPayment(PaymentStrategy):
    def pay(self, request, amount):
        # just a placeholder for PayPal integration
        return f"PayPal processed ${amount}"


class CashPayment(PaymentStrategy):
    def pay(self, request, amount):
        # in real case you might mark the bill as paid
        return f"Cash payment received: ${amount}"
