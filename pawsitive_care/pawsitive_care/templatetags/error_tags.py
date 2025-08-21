from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def safe_url(url_name, *args, **kwargs):
    """
    Safely resolve a URL name, returning None if it fails
    """
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        logger.warning(f"URL name '{url_name}' could not be resolved")
        return None


@register.simple_tag
def safe_url_with_fallback(url_name, fallback_url="/", *args, **kwargs):
    """
    Safely resolve a URL name, returning fallback if it fails
    """
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        logger.warning(f"URL name '{url_name}' could not be resolved, using fallback: {fallback_url}")
        return fallback_url


@register.inclusion_tag('components/safe_link.html')
def safe_link(url_name, link_text, css_class="btn btn-primary", icon_class="", fallback_url="/", *args, **kwargs):
    """
    Render a safe link that handles broken URLs gracefully
    """
    try:
        url = reverse(url_name, args=args, kwargs=kwargs)
        available = True
    except NoReverseMatch:
        url = fallback_url
        available = False
        logger.warning(f"URL name '{url_name}' could not be resolved")
    
    return {
        'url': url,
        'link_text': link_text,
        'css_class': css_class,
        'icon_class': icon_class,
        'available': available,
        'original_url_name': url_name
    }


@register.filter
def is_url_available(url_name):
    """
    Check if a URL name is available
    """
    try:
        reverse(url_name)
        return True
    except NoReverseMatch:
        return False


@register.simple_tag
def dashboard_url_for_user(user):
    """
    Get the appropriate dashboard URL for a user with fallback handling
    """
    if not user.is_authenticated:
        return None
    
    dashboard_mapping = {
        'is_admin': 'accounts:admin_dashboard',
        'is_vet': 'accounts:vet_dashboard', 
        'is_staff_member': 'accounts:staff_dashboard',
    }
    
    # Check user role and try to resolve appropriate dashboard
    for role_check, url_name in dashboard_mapping.items():
        if hasattr(user, role_check) and getattr(user, role_check)():
            try:
                return reverse(url_name)
            except NoReverseMatch:
                logger.warning(f"Dashboard URL '{url_name}' not available for user role")
                continue
    
    # Default to client dashboard
    try:
        return reverse('accounts:client_dashboard')
    except NoReverseMatch:
        logger.warning("Client dashboard URL not available")
        return None


@register.inclusion_tag('components/error_navigation.html')
def error_navigation(user, current_error_type=""):
    """
    Render context-aware navigation for error pages
    """
    nav_items = []
    
    # Always try to add home link
    try:
        home_url = reverse('home')
        nav_items.append({
            'url': home_url,
            'text': 'Return Home',
            'icon': 'fas fa-home',
            'class': 'btn btn-accent',
            'available': True
        })
    except NoReverseMatch:
        nav_items.append({
            'url': '/',
            'text': 'Return Home',
            'icon': 'fas fa-home', 
            'class': 'btn btn-accent',
            'available': False
        })
    
    if user.is_authenticated:
        # Add dashboard link
        dashboard_url = dashboard_url_for_user(user)
        if dashboard_url:
            dashboard_text = "Go to Dashboard"
            if hasattr(user, 'is_admin') and user.is_admin():
                dashboard_text = "Admin Dashboard"
            elif hasattr(user, 'is_vet') and user.is_vet():
                dashboard_text = "Vet Dashboard"
            elif hasattr(user, 'is_staff_member') and user.is_staff_member():
                dashboard_text = "Staff Dashboard"
            else:
                dashboard_text = "Client Dashboard"
                
            nav_items.append({
                'url': dashboard_url,
                'text': dashboard_text,
                'icon': 'fas fa-tachometer-alt',
                'class': 'btn btn-ghost',
                'available': True
            })
        else:
            nav_items.append({
                'url': '/',
                'text': 'Dashboard (Unavailable)',
                'icon': 'fas fa-tachometer-alt',
                'class': 'btn btn-ghost disabled',
                'available': False
            })
    
    return {
        'nav_items': nav_items,
        'user': user,
        'current_error_type': current_error_type
    }
