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
    from petmedia.models import BlogPost, BlogComment, BlogLike, BlogCategory
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    User = get_user_model()
    
    # User statistics
    total_users = User.objects.count()
    admin_count = User.objects.filter(role='admin').count()
    vet_count = User.objects.filter(role='vet').count()
    staff_count = User.objects.filter(role='staff').count()
    client_count = User.objects.filter(role='client').count()
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Blog statistics
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(is_published=True).count()
    unpublished_posts = BlogPost.objects.filter(is_published=False).count()
    featured_posts = BlogPost.objects.filter(is_featured=True).count()
    professional_posts = BlogPost.objects.filter(is_professional_advice=True).count()
    
    # Recent blog activity
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    recent_posts = BlogPost.objects.order_by('-created_at')[:5]
    posts_this_week = BlogPost.objects.filter(created_at__gte=week_ago).count()
    
    # Comment statistics
    total_comments = BlogComment.objects.count()
    pending_comments = BlogComment.objects.filter(is_approved=False).count()
    
    # Engagement statistics
    total_likes = BlogLike.objects.count()
    
    # Category statistics
    categories_with_counts = BlogCategory.objects.annotate(
        post_count=Count('blogpost')
    ).order_by('-post_count')[:5]
    
    # Inventory statistics
    from inventory.models import InventoryItem
    from django.db import models
    
    total_inventory_items = InventoryItem.objects.filter(is_active=True).count()
    low_stock_inventory = InventoryItem.objects.filter(
        quantity_in_stock__lte=models.F('minimum_stock_level'),
        is_active=True
    ).count()
    medicine_items = InventoryItem.objects.filter(category='MEDICINE', is_active=True).count()
    supply_items = InventoryItem.objects.filter(category='SUPPLY', is_active=True).count()
    
    # Appointment statistics
    try:
        from appointments.models import Appointment
        total_appointments = Appointment.objects.count()
        appointments_today = Appointment.objects.filter(date=today).count()
        appointments_this_week = Appointment.objects.filter(
            date__gte=week_ago
        ).count()
        completed_appointments = Appointment.objects.filter(status='COMPLETED').count()
        pending_appointments = Appointment.objects.filter(status='PENDING').count()
    except ImportError:
        total_appointments = 0
        appointments_today = 0
        appointments_this_week = 0
        completed_appointments = 0
        pending_appointments = 0
    
    # Billing statistics
    try:
        from billing.models import Billing
        from django.db.models import Sum
        total_bills = Billing.objects.count()
        pending_bills = Billing.objects.filter(status='pending').count()
        paid_bills = Billing.objects.filter(status='paid').count()
        total_revenue = Billing.objects.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        revenue_this_week = Billing.objects.filter(
            status='paid',
            issued_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
    except ImportError:
        total_bills = 0
        pending_bills = 0
        paid_bills = 0
        total_revenue = 0
        revenue_this_week = 0
    
    # Pet statistics
    try:
        from pets.models import Pet
        total_pets = Pet.objects.filter(is_active=True).count()
        new_pets_this_week = Pet.objects.filter(
            created_at__gte=week_ago,
            is_active=True
        ).count()
    except ImportError:
        total_pets = 0
        new_pets_this_week = 0
    
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
        'blog_stats': {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'unpublished_posts': unpublished_posts,
            'featured_posts': featured_posts,
            'professional_posts': professional_posts,
            'posts_this_week': posts_this_week,
            'total_comments': total_comments,
            'pending_comments': pending_comments,
            'total_likes': total_likes,
        },
        'inventory_stats': {
            'total_items': total_inventory_items,
            'low_stock_items': low_stock_inventory,
            'medicine_items': medicine_items,
            'supply_items': supply_items,
        },
        'appointment_stats': {
            'total_appointments': total_appointments,
            'appointments_today': appointments_today,
            'appointments_this_week': appointments_this_week,
            'completed_appointments': completed_appointments,
            'pending_appointments': pending_appointments,
        },
        'billing_stats': {
            'total_bills': total_bills,
            'pending_bills': pending_bills,
            'paid_bills': paid_bills,
            'total_revenue': total_revenue,
            'revenue_this_week': revenue_this_week,
        },
        'pet_stats': {
            'total_pets': total_pets,
            'new_pets_this_week': new_pets_this_week,
        },
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'top_categories': categories_with_counts,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@vet_required
def vet_dashboard(request):
    from inventory.models import InventoryItem
    from pets.models import Pet
    from django.utils import timezone
    from django.db import models
    from datetime import timedelta
    
    # Get inventory statistics
    medicine_count = InventoryItem.objects.filter(category='MEDICINE', is_active=True).count()
    supply_count = InventoryItem.objects.filter(category='SUPPLY', is_active=True).count()
    low_stock_items = InventoryItem.objects.filter(
        quantity_in_stock__lte=models.F('minimum_stock_level'),
        is_active=True
    ).count()
    
    # Get inventory alerts
    inventory_alerts = []
    
    # Low stock alerts
    low_stock = InventoryItem.objects.filter(
        quantity_in_stock__lte=models.F('minimum_stock_level'),
        is_active=True
    )[:3]
    
    for item in low_stock:
        inventory_alerts.append({
            'type': 'low_stock',
            'message': f"{item.name} is low in stock ({item.quantity_in_stock} left)"
        })
    
    # Expiring items
    cutoff_date = timezone.now().date() + timedelta(days=30)
    expiring_items = InventoryItem.objects.filter(
        expiry_date__lte=cutoff_date,
        expiry_date__isnull=False,
        is_active=True
    )[:2]
    
    for item in expiring_items:
        days_until_expiry = (item.expiry_date - timezone.now().date()).days
        inventory_alerts.append({
            'type': 'expiring',
            'message': f"{item.name} expires in {days_until_expiry} days"
        })
    
    # Out of stock items
    out_of_stock = InventoryItem.objects.filter(
        quantity_in_stock=0,
        is_active=True
    )[:2]
    
    for item in out_of_stock:
        inventory_alerts.append({
            'type': 'out_of_stock',
            'message': f"{item.name} is out of stock"
        })
    
    # Get patient statistics
    total_patients = Pet.objects.filter(is_active=True).count()
    dogs_count = Pet.objects.filter(is_active=True, species__icontains='dog').count()
    cats_count = Pet.objects.filter(is_active=True, species__icontains='cat').count()
    other_pets_count = total_patients - dogs_count - cats_count
    
    # Get new patients this month
    first_day_of_month = timezone.now().replace(day=1).date()
    new_this_month = Pet.objects.filter(
        is_active=True,
        created_at__gte=first_day_of_month
    ).count()
    
    # Get vet's appointments for today and this week
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    try:
        from appointments.models import Appointment
        todays_appointments = Appointment.objects.filter(
            vet=request.user,
            date=today
        ).select_related('client', 'pet').order_by('time')
        
        weekly_appointments = Appointment.objects.filter(
            vet=request.user,
            date__gte=week_ago,
            date__lte=today
        ).count()
        
        completed_this_week = Appointment.objects.filter(
            vet=request.user,
            date__gte=week_ago,
            date__lte=today,
            status='COMPLETED'
        ).count()
    except ImportError:
        todays_appointments = []
        weekly_appointments = 0
        completed_this_week = 0
    
    # Get recent blog posts for the community section
    try:
        from petmedia.models import BlogPost
        recent_blog_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:5]
        
        # Get vet's professional posts count
        vet_posts_count = BlogPost.objects.filter(
            author=request.user,
            is_professional_advice=True
        ).count()
    except ImportError:
        recent_blog_posts = []
        vet_posts_count = 0
    
    # Get recent medical records or cases
    try:
        from records.models import MedicalRecord
        recent_cases = MedicalRecord.objects.filter(
            vet=request.user
        ).select_related('pet', 'pet__owner').order_by('-created_at')[:5]
    except ImportError:
        recent_cases = []
    
    # Get billing statistics for vet
    try:
        from billing.models import Billing
        # Bills for appointments with this vet
        vet_bills = Billing.objects.filter(
            appointment__vet=request.user
        )
        total_vet_bills = vet_bills.count()
        pending_vet_bills = vet_bills.filter(status='pending').count()
        
        # Revenue from vet's services this week
        from django.db.models import Sum
        week_ago = today - timedelta(days=7)
        weekly_revenue = vet_bills.filter(
            status='paid',
            paid_at__gte=week_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
    except ImportError:
        total_vet_bills = 0
        pending_vet_bills = 0
        weekly_revenue = 0

    context = {
        'title': 'Veterinarian Dashboard',
        'user_role': 'Veterinarian',
        'inventory_stats': {
            'medicine_count': medicine_count,
            'supply_count': supply_count,
            'low_stock_items': low_stock_items,
        },
        'inventory_alerts': inventory_alerts,
        'patient_stats': {
            'total_patients': total_patients,
            'dogs_count': dogs_count,
            'cats_count': cats_count,
            'other_pets_count': other_pets_count,
            'new_this_month': new_this_month,
            'weekly_appointments': weekly_appointments,
            'completed_this_week': completed_this_week,
            'vet_posts_count': vet_posts_count,
        },
        'billing_stats': {
            'total_bills': total_vet_bills,
            'pending_bills': pending_vet_bills,
            'weekly_revenue': weekly_revenue,
        },
        'todays_appointments': todays_appointments,
        'recent_blog_posts': recent_blog_posts,
        'recent_cases': recent_cases,
    }
    return render(request, 'accounts/vet_dashboard.html', context)


@staff_required
def staff_dashboard(request):
    from inventory.models import InventoryItem
    from pets.models import Pet
    from django.contrib.auth import get_user_model
    from django.db import models
    from django.utils import timezone
    from datetime import timedelta, date
    
    User = get_user_model()
    
    # Inventory statistics
    total_items = InventoryItem.objects.filter(is_active=True).count()
    low_stock_items = InventoryItem.objects.filter(
        quantity_in_stock__lte=models.F('minimum_stock_level'),
        is_active=True
    ).count()
    
    # Weekly statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Try to get appointment statistics
    try:
        from appointments.models import Appointment
        total_appointments = Appointment.objects.filter(
            date__gte=week_ago,
            date__lte=today
        ).count()
        completed_appointments = Appointment.objects.filter(
            date__gte=week_ago,
            date__lte=today,
            status='COMPLETED'
        ).count()
        
        # Today's appointments
        todays_appointments = Appointment.objects.filter(
            date=today
        ).select_related('client', 'pet', 'vet').order_by('time')[:5]
    except ImportError:
        total_appointments = 0
        completed_appointments = 0
        todays_appointments = []
    
    # Client statistics
    new_clients_this_week = User.objects.filter(
        role='client',
        date_joined__gte=week_ago
    ).count()
    
    total_clients = User.objects.filter(role='client').count()
    total_pets = Pet.objects.filter(is_active=True).count()
    
    # Billing statistics
    try:
        from billing.models import Billing
        pending_bills = Billing.objects.filter(status='pending').count()
        total_revenue_this_week = Billing.objects.filter(
            issued_at__gte=week_ago,
            status='paid'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    except ImportError:
        pending_bills = 0
        total_revenue_this_week = 0
    
    context = {
        'title': 'Staff Dashboard',
        'user_role': 'Staff Member',
        'weekly_stats': {
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'new_clients': new_clients_this_week,
            'revenue': total_revenue_this_week,
        },
        'inventory_stats': {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
        },
        'general_stats': {
            'total_clients': total_clients,
            'total_pets': total_pets,
            'pending_bills': pending_bills,
        },
        'todays_appointments': todays_appointments,
    }
    return render(request, 'accounts/staff_dashboard.html', context)


@login_required
def client_dashboard(request):
    from pets.models import Pet
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user's pets
    user_pets = Pet.objects.filter(owner=request.user, is_active=True)
    total_pets = user_pets.count()
    
    # Get pet statistics by species
    pet_stats = {}
    for pet in user_pets:
        species = pet.get_species_display() if pet.species else 'Unknown'
        pet_stats[species] = pet_stats.get(species, 0) + 1
    
    # Get appointment data for the user
    today = timezone.now().date()
    week_from_now = today + timedelta(days=7)
    
    try:
        from appointments.models import Appointment
        
        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            client=request.user,
            date__gte=today
        ).select_related('pet', 'vet').order_by('date', 'time')[:5]
        
        # Recent appointments
        recent_appointments = Appointment.objects.filter(
            client=request.user,
            date__lt=today
        ).select_related('pet', 'vet').order_by('-date', '-time')[:3]
        
        # Appointment statistics
        total_appointments = Appointment.objects.filter(client=request.user).count()
        completed_appointments = Appointment.objects.filter(
            client=request.user,
            status='COMPLETED'
        ).count()
        
        # Appointments this month
        month_start = today.replace(day=1)
        appointments_this_month = Appointment.objects.filter(
            client=request.user,
            date__gte=month_start
        ).count()
        
    except ImportError:
        upcoming_appointments = []
        recent_appointments = []
        total_appointments = 0
        completed_appointments = 0
        appointments_this_month = 0
    
    # Get billing information
    try:
        from billing.models import Billing
        
        # Outstanding bills
        outstanding_bills = Billing.objects.filter(
            owner=request.user,
            status='pending'
        ).order_by('-issued_at')[:3]
        
        # Billing statistics
        total_bills = Billing.objects.filter(owner=request.user).count()
        paid_bills = Billing.objects.filter(
            owner=request.user,
            status='paid'
        ).count()
        
        # Total amount owed
        from django.db.models import Sum
        amount_owed = Billing.objects.filter(
            owner=request.user,
            status='pending'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
    except ImportError:
        outstanding_bills = []
        total_bills = 0
        paid_bills = 0
        amount_owed = 0
    
    # Get blog posts for community engagement
    try:
        from petmedia.models import BlogPost
        
        # Recent blog posts
        recent_blog_posts = BlogPost.objects.filter(
            is_published=True
        ).order_by('-created_at')[:5]
        
        # User's blog posts
        user_blog_posts = BlogPost.objects.filter(
            author=request.user
        ).count()
        
    except ImportError:
        recent_blog_posts = []
        user_blog_posts = 0
    
    # Get medical records for pets
    try:
        from records.models import MedicalRecord
        
        recent_medical_records = MedicalRecord.objects.filter(
            pet__owner=request.user
        ).select_related('pet', 'vet').order_by('-created_at')[:5]
        
    except ImportError:
        recent_medical_records = []
    
    # Pet health alerts (upcoming vaccinations, checkups, etc.)
    pet_alerts = []
    for pet in user_pets[:3]:  # Limit to first 3 pets for dashboard
        # Use age field for general health reminders
        if pet.age:
            if pet.age >= 1 and pet.age < 7:  # Adult pets
                pet_alerts.append({
                    'pet': pet.name,
                    'message': f"Annual checkup recommended for {pet.name}",
                    'type': 'checkup'
                })
            elif pet.age >= 7:  # Senior pets
                pet_alerts.append({
                    'pet': pet.name,
                    'message': f"Senior pet checkup recommended for {pet.name}",
                    'type': 'senior_care'
                })
    
    context = {
        'title': 'Client Dashboard',
        'user_role': 'Pet Owner',
        'pet_stats': {
            'total_pets': total_pets,
            'pet_breakdown': pet_stats,
        },
        'user_pets': user_pets[:6],  # Show first 6 pets
        'appointment_stats': {
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'appointments_this_month': appointments_this_month,
        },
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'billing_stats': {
            'total_bills': total_bills,
            'paid_bills': paid_bills,
            'amount_owed': amount_owed,
        },
        'outstanding_bills': outstanding_bills,
        'recent_blog_posts': recent_blog_posts,
        'user_blog_posts': user_blog_posts,
        'recent_medical_records': recent_medical_records,
        'pet_alerts': pet_alerts,
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


# User detail view (admin only)
@admin_required
def user_detail(request, user_id):
    """View individual user details (admin only)"""
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    User = get_user_model()
    
    user = get_object_or_404(User, id=user_id)
    
    # Get user's pets if they have any
    user_pets = []
    try:
        from pets.models import Pet
        user_pets = Pet.objects.filter(owner=user, is_active=True)
    except ImportError:
        pass
    
    # Get user's appointments if they have any
    user_appointments = []
    try:
        from appointments.models import Appointment
        user_appointments = Appointment.objects.filter(client=user).order_by('-date')[:5]
    except ImportError:
        pass
    
    # Get user's billing if they have any
    user_bills = []
    try:
        from billing.models import Billing
        user_bills = Billing.objects.filter(owner=user).order_by('-issued_at')[:5]
    except ImportError:
        pass
    
    context = {
        'user_detail': user,
        'user_pets': user_pets,
        'user_appointments': user_appointments,
        'user_bills': user_bills,
    }
    return render(request, 'accounts/user_detail.html', context)


# User edit view (admin only)
@admin_required
def user_edit(request, user_id):
    """Edit user details (admin only)"""
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    User = get_user_model()
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        user.phone = request.POST.get('phone', user.phone)
        user.is_active = 'is_active' in request.POST
        
        try:
            user.save()
            messages.success(request, f'User {user.get_full_name() or user.username} updated successfully.')
            return redirect('accounts:user_detail', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'user_edit': user,
        'role_choices': User.ROLE_CHOICES if hasattr(User, 'ROLE_CHOICES') else [
            ('client', 'Client'),
            ('staff', 'Staff'),
            ('vet', 'Veterinarian'),
            ('admin', 'Administrator'),
        ]
    }
    return render(request, 'accounts/user_edit.html', context)


# User delete view (admin only)
@admin_required
def user_delete(request, user_id):
    """Delete user (admin only)"""
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    User = get_user_model()
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deleting themselves
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:user_management')
    
    if request.method == 'POST':
        user_name = user.get_full_name() or user.username
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                user.delete()
                return JsonResponse({
                    'success': True, 
                    'message': f'User {user_name} deleted successfully.'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'message': f'Error deleting user: {str(e)}'
                })
        
        # Handle regular form submission
        try:
            user.delete()
            messages.success(request, f'User {user_name} deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
        
        return redirect('accounts:user_management')
    
    context = {
        'user_delete': user,
    }
    return render(request, 'accounts/user_delete.html', context)


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
