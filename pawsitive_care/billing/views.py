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

User = get_user_model()
repository = BillingRepository()
factory = BillingFactory()

# Observer setup
billing_subject = BillingSubject()
billing_subject.attach(EmailNotifier())
billing_subject.attach(SMSNotifier())
@login_required
def add_bill(request):
    # Only allow staff and admin to create bills
    if not (request.user.is_staff or request.user.is_admin):
        return HttpResponseForbidden("You don't have permission to create bills.")
    
    appointments = Appointment.objects.filter(status="COMPLETED")
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
    return render(request, "Add_bill.html", {
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
    # Staff, admin, and vets can view all bills; regular users see only their own
    if request.user.is_staff or request.user.is_admin or request.user.is_vet:
        bills = Billing.objects.all()
        title = "All Bills"
    else:
        bills = Billing.objects.filter(owner=request.user)
        title = "My Bills"
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bills = bills.filter(status=status_filter)
        title = f"{title} - {status_filter.title()}"
    
    bills = bills.order_by('-issued_at')

    return render(request, "view_bill.html", {
        "bills": bills,
        "title": title
    })



@login_required
def my_bills(request):
    bills = repository.get_bills_by_owner(request.user)
    return render(request, "my_bills.html", {
        "bills": bills,
        "title": "My Bills"
    })

@login_required
def pay_bill(request, billing_id):
    billing = get_object_or_404(Billing, billing_id=billing_id, owner=request.user)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")
        
        if payment_method not in ["cash", "stripe", "paypal"]:
            messages.error(request, "Invalid payment method.")
        else:
            # Here you would integrate actual payment gateway logic for Stripe/PayPal
            billing.mark_as_paid()
            messages.success(request, f"Payment successful! Billing ID: {billing.billing_id}")
            return redirect("billing:view_bills")

    # Use utility function to calculate total safely
    total_amount = calculate_total(billing.amount)

    return render(request, "pay_bill.html", {
        "billing": billing,
        "total_amount": total_amount,
    })
@login_required
def delete_bill(request, billing_id):
    bill = get_object_or_404(Billing, billing_id=billing_id)

    if request.user != bill.veterian and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to delete this bill.")

    if request.method == "POST":
        bill.delete()
        messages.success(request, "Bill deleted successfully.")
        return redirect('billing:view_bills')

    return render(request, "billing_confirm_delete.html", {"bill": bill})
















































#servicecost_list (never change)

# ADD/ Update ServiceCost
@login_required
@csrf_exempt
def servicecost_list(request):
    # Only allow staff, admin, or vet to access service cost management
    if not (request.user.is_staff or request.user.is_admin or request.user.is_vet):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
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
    return render(request, 'my_bills.html', context)