from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def records_list(request):
    return render(request, 'records/records_list.html', {
        'title': 'Records'
    })
