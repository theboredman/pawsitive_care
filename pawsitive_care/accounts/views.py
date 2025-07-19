from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from .decorators import (
    admin_required, vet_required, staff_required, 
    admin_or_vet_required, AdminRequiredMixin, 
    VetRequiredMixin, AdminOrVetRequiredMixin
)

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Specify the backend explicitly to avoid multiple backends error
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        
        # Add success message and redirect to appropriate dashboard
        messages.success(self.request, 'Registration successful! Welcome to Pawsitive Care!')
        return redirect('accounts:client_dashboard')  # New clients go to client dashboard

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        
        messages.success(self.request, f'Welcome back, {user.get_role_display()}!')
        
        if user.is_admin():
            return redirect('accounts:admin_dashboard')
        elif user.is_vet():
            return redirect('accounts:vet_dashboard')
        elif user.is_staff_member():
            return redirect('accounts:staff_dashboard')
        else:  # client
            return redirect('accounts:client_dashboard')
        
        return response

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# Role-based Dashboard Views
@admin_required
def admin_dashboard(request):
    """Admin-only dashboard"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    total_users = User.objects.count()
    admin_count = User.objects.filter(role='admin').count()
    vet_count = User.objects.filter(role='vet').count()
    staff_count = User.objects.filter(role='staff').count()
    client_count = User.objects.filter(role='client').count()
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'title': 'Admin Dashboard',
        'user_role': 'Administrator',
        'stats': {
            'total_users': total_users,
            'admin_count': admin_count,
            'vet_count': vet_count,
            'staff_count': staff_count,
            'client_count': client_count,
        },
        'recent_users': recent_users,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@vet_required
def vet_dashboard(request):
    context = {
        'title': 'Veterinarian Dashboard',
        'user_role': 'Veterinarian'
    }
    return render(request, 'accounts/vet_dashboard.html', context)


@staff_required
def staff_dashboard(request):
    context = {
        'title': 'Staff Dashboard',
        'user_role': 'Staff Member'
    }
    return render(request, 'accounts/staff_dashboard.html', context)


@login_required
def client_dashboard(request):
    context = {
        'title': 'Client Dashboard',
        'user_role': 'Client'
    }
    return render(request, 'accounts/client_dashboard.html', context)


# Class-based views with role protection
class AdminOnlyView(AdminRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/admin_only.html')


class VetOnlyView(VetRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/vet_only.html')


class AdminOrVetView(AdminOrVetRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/admin_or_vet.html')


# User management view (admin only)
@admin_required
def user_management(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    users = User.objects.all().order_by('-date_joined')
    
    total_users = users.count()
    admin_count = users.filter(role='admin').count()
    vet_count = users.filter(role='vet').count()
    staff_count = users.filter(role='staff').count()
    client_count = users.filter(role='client').count()
    
    context = {
        'users': users,
        'stats': {
            'total_users': total_users,
            'admin_count': admin_count,
            'vet_count': vet_count,
            'staff_count': staff_count,
            'client_count': client_count,
        }
    }
    return render(request, 'accounts/user_management.html', context)


# Client promotion view (admin only)
@admin_required
def promote_clients(request):
    """View to promote clients to staff members (admin only)"""
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    User = get_user_model()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'promote_to_staff':
                user.role = 'staff'
                user.save()
                messages.success(request, f'{user.get_full_name() or user.username} has been promoted to staff member.')
            elif action == 'promote_to_vet':
                user.role = 'vet'
                user.save()
                messages.success(request, f'{user.get_full_name() or user.username} has been promoted to veterinarian.')
            elif action == 'demote_to_client':
                user.role = 'client'
                user.save()
                messages.success(request, f'{user.get_full_name() or user.username} has been demoted to client.')
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'User role updated to {user.get_role_display()}',
                    'new_role': user.get_role_display(),
                    'new_role_code': user.role
                })
                
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'User not found.'})
        
        return redirect('accounts:promote_clients')
    
    # Get all users grouped by role
    clients = User.objects.filter(role='client').order_by('first_name', 'last_name', 'username')
    staff_members = User.objects.filter(role='staff').order_by('first_name', 'last_name', 'username')
    vets = User.objects.filter(role='vet').order_by('first_name', 'last_name', 'username')
    
    # Calculate statistics
    stats = {
        'client_count': clients.count(),
        'staff_count': staff_members.count(),
        'vet_count': vets.count(),
        'total_promotable': clients.count(),
    }
    
    context = {
        'clients': clients,
        'staff_members': staff_members,
        'vets': vets,
        'stats': stats,
    }
    return render(request, 'accounts/promote_clients.html', context)
