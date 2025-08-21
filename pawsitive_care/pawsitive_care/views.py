from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest


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


# Custom error handlers
def custom_404_view(request, exception=None):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)


def custom_403_view(request, exception=None):
    """Custom 403 error page"""
    return render(request, '403.html', status=403)


def custom_400_view(request, exception=None):
    """Custom 400 error page"""
    return render(request, '400.html', status=400)


# Test views to trigger errors (for testing purposes only)
def test_404_view(request):
    """Test view to trigger a 404 error"""
    return HttpResponseNotFound(render(request, '404.html'))


def test_500_view(request):
    """Test view to trigger a 500 error"""
    raise Exception("This is a test 500 error")


def test_403_view(request):
    """Test view to trigger a 403 error"""
    return HttpResponseForbidden(render(request, '403.html'))


def test_400_view(request):
    """Test view to trigger a 400 error"""
    return HttpResponseBadRequest(render(request, '400.html'))


def test_errors_page(request):
    """Show test page with links to all error pages"""
    return render(request, 'test_errors.html')


def test_safe_urls(request):
    """Test safe URL handling functionality"""
    return render(request, 'test_safe_urls.html')
