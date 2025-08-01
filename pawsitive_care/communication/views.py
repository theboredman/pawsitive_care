from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def communication_list(request):
    return render(request, 'communication/communication_list.html', {
        'title': 'Communication'
    })
