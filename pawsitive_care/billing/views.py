# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Billing
from .patterns.strategy import StripePayment, PaypalPayment, CashPayment
from django.shortcuts import render



def billing_list(request):
    """List all billing records"""
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=400)

    bills = Billing.objects.all().order_by('-issued_at')
    data = [
        {
            "billing_id": b.billing_id,
            "owner": b.owner.username,
            "pet": b.pet.name,
            "amount": str(b.amount),
            "status": b.status,
            "issued_at": b.issued_at,
        } for b in bills
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def billing_create(request):
    """Create a billing record"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    required_fields = ["owner_id", "pet_id", "amount"]
    for field in required_fields:
        if field not in data:
            return JsonResponse({"error": f"'{field}' is required."}, status=400)

    billing = Billing.objects.create(
        owner_id=data["owner_id"],
        pet_id=data["pet_id"],
        amount=data["amount"],
        description=data.get("description", "")
    )

    return JsonResponse({"billing_id": billing.billing_id, "status": billing.status}, status=201)


def billing_detail(request, billing_id):
    """Retrieve billing details"""
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=400)

    try:
        billing = Billing.objects.get(billing_id=billing_id)
    except Billing.DoesNotExist:
        return JsonResponse({"error": "Billing not found."}, status=404)

    data = {
        "billing_id": billing.billing_id,
        "owner": billing.owner.username,
        "pet": billing.pet.name,
        "amount": str(billing.amount),
        "status": billing.status,
        "issued_at": billing.issued_at,
        "paid_at": billing.paid_at,
        "description": billing.description,
    }
    return JsonResponse(data)


@csrf_exempt
def billing_update(request, billing_id):
    """Update billing record"""
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error": "PUT or PATCH request required"}, status=400)

    try:
        billing = Billing.objects.get(billing_id=billing_id)
    except Billing.DoesNotExist:
        return JsonResponse({"error": "Billing not found."}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    for field in ["amount", "description"]:
        if field in data:
            setattr(billing, field, data[field])

    billing.save()
    return JsonResponse({"billing_id": billing.billing_id, "status": billing.status})


@csrf_exempt
def billing_delete(request, billing_id):
    """Delete billing record"""
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, status=400)

    try:
        billing = Billing.objects.get(billing_id=billing_id)
        billing.delete()
    except Billing.DoesNotExist:
        return JsonResponse({"error": "Billing not found."}, status=404)

    return JsonResponse({"message": "Billing deleted successfully."}, status=204)


@csrf_exempt
def mark_billing_paid(request, billing_id):
    """Mark a billing record as paid"""
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        billing = Billing.objects.get(billing_id=billing_id)
        billing.mark_as_paid()  # Make sure your model has this method
    except Billing.DoesNotExist:
        return JsonResponse({"error": "Billing not found."}, status=404)

    return JsonResponse({"billing_id": billing.billing_id, "status": billing.status})

MOCK_BILLING = {
    "billing_id": 1,
    "pet_name": "Fluffy",
    "owner_name": "Alice",
    "amount": 50.0,
    "status": "unpaid"
}

def pay_bill(request):
    billing = MOCK_BILLING  # use mock billing for testing

    if request.method == "POST":
        method = request.POST.get("method")
        amount = billing["amount"]

        # Select payment strategy
        if method == "card":
            payment = StripePayment()
        elif method == "paypal":
            payment = PaypalPayment()
        elif method == "cash":
            payment = CashPayment()
        else:
            return render(request, "pay_bill.html", {"billing": billing, "error": "Select a payment method."})

        # Pass request and amount for Stripe; other strategies can ignore request
        if method == "card":
          return payment.pay(request, amount)  # This is an HttpResponseRedirect to Stripe
        else:
         result = payment.pay(amount)
        billing["status"] = "paid"
        return render(request, "pay_bill.html", {"billing": billing, "result": result})
        billing["status"] = "paid"
        return render(request, "pay_bill.html", {"billing": billing, "result": result})

    return render(request, "pay_bill.html", {"billing": billing})
