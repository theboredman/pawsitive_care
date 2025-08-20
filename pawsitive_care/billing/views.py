from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from .patterns.facade import BillingFacade
from .patterns.factory import BillingFactory
from .patterns.repositories import BillingRepository
from .patterns.observer import BillingSubject, EmailNotifier, SMSNotifier
from .patterns.strategy import StripePayment, PaypalPayment, CashPayment
from .models import Billing,ServiceCost
from pets.models import Pet
from appointments.models import Appointment
from .utils import calculate_total
from .forms import ServiceCostForm
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone



User = get_user_model()
repository = BillingRepository()
factory = BillingFactory()

# Observer setup
billing_subject = BillingSubject()
billing_subject.attach(EmailNotifier())
billing_subject.attach(SMSNotifier())
@login_required
def add_bill(request):
    appointments = Appointment.objects.filter(
        status="COMPLETED"
    ).exclude(
        billing__isnull=False  # exclude appointments that already have a billing
    )   
    selected_appointment = None
    pet = None
    owner = None
    service = None
    amount = None

    if request.method == "POST":
        appointment_id = request.POST.get("appointment")

        if "select_appointment" in request.POST:
            try:
                
                selected_appointment = Appointment.objects.get(appointment_id=appointment_id)
                pet = selected_appointment.pet
                owner = selected_appointment.client

                # Auto-select service based on appointment type
                service = ServiceCost.objects.filter(service_type=selected_appointment.appointment_type).first()
                amount = service.cost if service else 0.0

            except Appointment.DoesNotExist:
                messages.error(request, "Invalid appointment selected.")

        else:  # Final bill submission
            try:
                appointment = Appointment.objects.get(appointment_id=appointment_id)

                if hasattr(appointment, 'billing'):
                    messages.error(request, "This appointment already has a bill.")
                else:
                    pet = appointment.pet
                    owner = appointment.client

                    service_id = request.POST.get("service")
                    service = ServiceCost.objects.get(id=service_id)

                    amount = request.POST.get("amount") or service.cost

                    billing = Billing.objects.create(
                        appointment=appointment,
                        pet=pet,
                        owner=owner,
                        service=service,
                        amount=amount
                    )
                    messages.success(request, f"Bill added successfully! Billing ID: {billing.billing_id}")
                    return redirect(f"{reverse('billing:add_bill')}?success=1&billing_id={billing.billing_id}")

            except Appointment.DoesNotExist:
                messages.error(request, "Appointment not found.")
            except ServiceCost.DoesNotExist:
                messages.error(request, "Selected service not found.")
            except Exception as e:
                messages.error(request, f"Error adding bill: {str(e)}")

    services = ServiceCost.objects.all()
    return render(request, "add_bill.html", {
        "appointments": appointments,
        "selected_appointment": selected_appointment,
        "pet": pet,
        "owner": owner,
        "service": service,
        "amount": amount,
        "services": services,
        "success": request.GET.get("success") == "1",
        "billing_id": request.GET.get("billing_id"),
    })




@login_required
def view_bills(request):
    # Show only bills for the logged-in user
    bills = Billing.objects.filter(owner=request.user).order_by('-issued_at')

    return render(request, "view_bill.html", {
        "bills": bills,
        "title": "My Bills"
    })


@login_required
def my_bills(request):
    HttpResponseForbidden("You are not allowed to view this page.")
@login_required
def pay_bill(request, billing_id):
    billing = get_object_or_404(Billing, billing_id=billing_id, owner=request.user)
    total_amount = calculate_total(billing.amount)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        strategies = {
            "stripe": StripePayment(),
            "paypal": PaypalPayment(),
            "cash": CashPayment(),
        }

        if payment_method not in strategies:
            messages.error(request, "Invalid payment method.")
        else:
            strategy = strategies[payment_method]
            result = strategy.pay(request, total_amount)

            if payment_method in ["cash", "paypal"]:
                repository.update_status(billing.billing_id, "paid", timezone.now())
                messages.success(request, f"{payment_method.capitalize()} payment successful! Billing ID: {billing.billing_id}")
                return redirect("billing:view_bills")
            else:
                return result

    return render(request, "pay_bill.html", {
        "billing": billing,
        "total_amount": total_amount,
    })


    #With stripe

@login_required
def delete_bill(request, billing_id):
    bill = get_object_or_404(Billing, billing_id=billing_id)

    if request.user != bill.veterian and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to delete this bill.")

    if request.method == "POST":
        bill.delete()
        messages.success(request, "Bill deleted successfully.")
        return redirect('billing:view_bills')

    return render(request, "service/confirm_delete.html", {"bill": bill})

def payment_success(request):
    billing_id = request.GET.get('billing_id')
    session_id = request.GET.get('session_id')
    status = request.GET.get('status', 'success')

    if status == 'success' and billing_id:
        billing = Billing.objects.get(billing_id=billing_id)
        billing.status = 'paid'
        billing.paid_at = timezone.now()
        billing.save()
        messages.success(request, f"Payment successful for Billing ID {billing_id}!")
    else:
        messages.error(request, "Payment was canceled or failed.")

    return redirect('billing:view')














































#servicecost_list (never change)

# ADD/ Update ServiceCost
@csrf_exempt
def servicecost_list(request):
    # Get all service types
    service_choices = Appointment.APPOINTMENT_TYPES
    # Ensure each service type has a ServiceCost entry
    for key, label in service_choices:
        ServiceCost.objects.get_or_create(service_type=key, defaults={'cost': 0})

    # Fetch all ServiceCost objects ordered by service_type
    servicecosts = ServiceCost.objects.all().order_by('service_type')

    if request.method == 'POST':
        # Loop through each service type and update cost
        for sc in servicecosts:
            cost = request.POST.get(f'cost_{sc.service_type}')
            if cost is not None:
                try:
                    sc.cost = float(cost)
                    sc.save()
                except ValueError:
                    messages.error(request, f"Invalid cost for {sc.get_service_type_display()}")
        messages.success(request, "All service costs updated successfully!")
        return redirect('billing:servicecost_list')

    context = {
        'servicecosts': servicecosts,
    }
    return render(request, 'service/servicecost_list.html', context)

def servicecost_delete(request, pk):
    sc = get_object_or_404(ServiceCost, pk=pk)
    sc.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect('billing:servicecost_list')

@login_required
def my_bills(request):
    # Filter bills by logged-in user
    bills = Billing.objects.filter(owner=request.user).order_by('-issued_at')

    context = {
        'bills': bills
    }
    return render(request, 'billing/my_bills.html', context)