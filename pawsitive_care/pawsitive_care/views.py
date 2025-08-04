from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home_view(request):
    """
    Root page view for Pawsitive Care
    Shows welcome page for unauthenticated users
    Redirects authenticated users to their respective dashboards
    """
    if request.user.is_authenticated:
        # Redirect authenticated users to their appropriate dashboard
        if request.user.is_admin():
            return redirect('accounts:admin_dashboard')
        elif request.user.is_vet():
            return redirect('accounts:vet_dashboard')
        elif request.user.is_staff_member():
            return redirect('accounts:staff_dashboard')
        else:
            return redirect('accounts:client_dashboard')
    
    # Show welcome page for unauthenticated users
    return render(request, 'home.html')
