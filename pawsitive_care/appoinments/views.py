from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def appointment_list(request):
    return render(request, 'appoinments/appointment_list.html', {
        'title': 'Appointments'
    })
