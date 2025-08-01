from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def inventory_list(request):
    return render(request, 'inventory/inventory_list.html', {
        'title': 'Inventory'
    })
