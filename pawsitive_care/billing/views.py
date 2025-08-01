from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def billing_list(request):
    return render(request, 'billing/billing_list.html', {
        'title': 'Billing'
    })
