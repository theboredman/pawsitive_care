from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
import requests


class Command(BaseCommand):
    help = 'Test all error pages to ensure they work correctly'

    def handle(self, *args, **options):
        base_url = 'http://127.0.0.1:8000'
        
        # Test URLs and expected status codes
        test_cases = [
            ('/test-404/', 404, '404 Error Page'),
            ('/test-500/', 500, '500 Error Page'), 
            ('/test-403/', 403, '403 Error Page'),
            ('/test-400/', 400, '400 Error Page'),
            ('/non-existent-url/', 404, 'Real 404 Error'),
        ]
        
        self.stdout.write(self.style.SUCCESS('Testing Error Pages...'))
        self.stdout.write('-' * 50)
        
        for url, expected_status, description in test_cases:
            try:
                response = requests.get(base_url + url, timeout=10)
                
                if response.status_code == expected_status:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {description}: {url} -> {response.status_code}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {description}: {url} -> {response.status_code} (expected {expected_status})')
                    )
                    
                # Check if response contains expected content
                if 'Pawsitive Care' in response.text:
                    self.stdout.write(f'  Content check: ✓ Contains "Pawsitive Care"')
                else:
                    self.stdout.write(f'  Content check: ✗ Missing "Pawsitive Care"')
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ {description}: {url} -> Connection Error: {e}')
                )
        
        self.stdout.write('-' * 50)
        self.stdout.write(self.style.SUCCESS('Error page testing completed!'))
