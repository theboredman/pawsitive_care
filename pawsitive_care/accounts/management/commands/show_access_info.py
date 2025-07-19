from django.core.management.base import BaseCommand
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Display admin and application URLs with access information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Pawsitive Care - Access Information ==='))
        self.stdout.write('')
        
        # Admin Access
        self.stdout.write(self.style.WARNING('🔐 DJANGO ADMIN ACCESS:'))
        self.stdout.write(f'   URL: http://127.0.0.1:8000/admin/')
        self.stdout.write(f'   Use the "admin" demo account with is_staff=True permissions')
        self.stdout.write('')
        
        # Application URLs
        self.stdout.write(self.style.SUCCESS('🌐 APPLICATION URLs:'))
        urls = [
            ('Login', '/accounts/login/', 'Public access'),
            ('Register', '/accounts/register/', 'Public access'),
            ('Admin Dashboard', '/accounts/admin-dashboard/', 'Admin role only'),
            ('Vet Dashboard', '/accounts/vet-dashboard/', 'Veterinarian role only'),
            ('Staff Dashboard', '/accounts/staff-dashboard/', 'Staff role only'),
            ('Client Dashboard', '/accounts/client-dashboard/', 'Authenticated users'),
            ('User Management', '/accounts/users/', 'Admin role only'),
            ('Profile', '/accounts/profile/', 'Authenticated users'),
        ]
        
        for name, url, access in urls:
            self.stdout.write(f'   {name}: http://127.0.0.1:8000{url} ({access})')
        
        self.stdout.write('')
        
        # Demo Accounts
        self.stdout.write(self.style.HTTP_INFO('👤 DEMO ACCOUNTS:'))
        demo_accounts = [
            ('Admin', 'admin', 'admin123', 'Full system administration'),
            ('Veterinarian', 'vet', 'vet123', 'Medical professional tools'),
            ('Staff', 'staff', 'staff123', 'Reception and scheduling'),
            ('Client', 'client', 'client123', 'Pet owner portal'),
        ]
        
        for role, username, password, description in demo_accounts:
            self.stdout.write(f'   {role}: {username} | {password} - {description}')
        
        self.stdout.write('')
        
        # User Statistics
        try:
            total_users = User.objects.count()
            admin_count = User.objects.filter(role='admin').count()
            vet_count = User.objects.filter(role='vet').count()
            staff_count = User.objects.filter(role='staff').count()
            client_count = User.objects.filter(role='client').count()
            
            self.stdout.write(self.style.HTTP_SUCCESS('📊 USER STATISTICS:'))
            self.stdout.write(f'   Total Users: {total_users}')
            self.stdout.write(f'   Administrators: {admin_count}')
            self.stdout.write(f'   Veterinarians: {vet_count}')
            self.stdout.write(f'   Staff Members: {staff_count}')
            self.stdout.write(f'   Clients: {client_count}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error retrieving user statistics: {e}'))
        
        self.stdout.write('')
        self.stdout.write('Ready to test! 🚀')
