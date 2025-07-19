from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import CustomUser

# Customize the admin site headers
admin.site.site_header = "Pawsitive Care Administration"
admin.site.site_title = "Pawsitive Care Admin"
admin.site.index_title = "Welcome to Pawsitive Care Administration"

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Add custom fields to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone', 'address', 'role'),
            'classes': ('wide',),
        }),
    )
    
    # Add fields to the creation form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'address', 'role'),
            'classes': ('wide',),
        }),
    )
    
    # Customize the list display
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'role_badge',
        'is_active', 
        'is_staff', 
        'date_joined'
    )
    
    # Add filters to the right sidebar
    list_filter = BaseUserAdmin.list_filter + ('role', 'date_joined')
    
    # Add search functionality
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    # Set default ordering
    ordering = ('-date_joined',)
    
    def role_badge(self, obj):
        """Display role as a colored badge"""
        colors = {
            'admin': '#dc3545',    # Red
            'vet': '#28a745',      # Green  
            'staff': '#ffc107',    # Yellow
            'client': '#17a2b8',   # Blue
        }
        color = colors.get(obj.role, '#6c757d')  # Default gray
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
    
    def get_queryset(self, request):
        """Optimize queries by selecting related fields"""
        return super().get_queryset(request).select_related()
    
    # Custom admin actions
    def make_admin(self, request, queryset):
        """Bulk action to make selected users admins"""
        count = queryset.update(role='admin')
        self.message_user(request, f'{count} users were successfully made administrators.')
    make_admin.short_description = "Make selected users administrators"
    
    def make_vet(self, request, queryset):
        """Bulk action to make selected users veterinarians"""
        count = queryset.update(role='vet')
        self.message_user(request, f'{count} users were successfully made veterinarians.')
    make_vet.short_description = "Make selected users veterinarians"
    
    def make_staff(self, request, queryset):
        """Bulk action to make selected users staff members"""
        count = queryset.update(role='staff')
        self.message_user(request, f'{count} users were successfully made staff members.')
    make_staff.short_description = "Make selected users staff members"
    
    def make_client(self, request, queryset):
        """Bulk action to make selected users clients"""
        count = queryset.update(role='client')
        self.message_user(request, f'{count} users were successfully made clients.')
    make_client.short_description = "Make selected users clients"
    
    def activate_users(self, request, queryset):
        """Bulk action to activate selected users"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} users were successfully activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Bulk action to deactivate selected users"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} users were successfully deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    # Register the actions
    actions = [
        'make_admin', 'make_vet', 'make_staff', 'make_client',
        'activate_users', 'deactivate_users'
    ]