"""
Test Configuration for Pawsitive Care
This file contains test-specific settings and configurations.
"""

import os
from django.test import TestCase
from django.test.utils import override_settings
import tempfile

# Test database settings
TEST_DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',  # Use in-memory database for faster tests
}

# Test media settings
TEST_MEDIA_ROOT = tempfile.mkdtemp()

# Test email settings
TEST_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Test settings decorator
def test_settings(func):
    """Decorator to apply test-specific settings"""
    return override_settings(
        DATABASES={'default': TEST_DATABASE_CONFIG},
        MEDIA_ROOT=TEST_MEDIA_ROOT,
        EMAIL_BACKEND=TEST_EMAIL_BACKEND,
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.MD5PasswordHasher',  # Faster for tests
        ],
        CELERY_TASK_ALWAYS_EAGER=True,  # Execute tasks synchronously in tests
        CELERY_TASK_EAGER_PROPAGATES=True,
    )(func)


class FastTestCase(TestCase):
    """Base test case with optimized settings for speed"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test optimizations"""
        super().setUpClass()
        # Any class-level setup can go here
        
    def setUp(self):
        """Set up method run before each test"""
        super().setUp()
        # Clear any cached data
        
    def tearDown(self):
        """Clean up method run after each test"""
        super().tearDown()
        # Clean up any test data


# Test data factories
class TestDataFactory:
    """Factory class for creating test data"""
    
    @staticmethod
    def create_test_user(username="testuser", role="client", **kwargs):
        """Create a test user with default values"""
        from accounts.models import CustomUser
        
        defaults = {
            'email': f'{username}@test.com',
            'phone': '1234567890',
            'address': '123 Test St',
            'first_name': 'Test',
            'last_name': 'User',
        }
        defaults.update(kwargs)
        
        return CustomUser.objects.create_user(
            username=username,
            password='testpass123',
            role=role,
            **defaults
        )
    
    @staticmethod
    def create_test_pet(owner, name="TestPet", **kwargs):
        """Create a test pet with default values"""
        from pets.models import Pet
        
        defaults = {
            'species': 'DOG',
            'breed': 'Test Breed',
            'age': 3,
            'gender': 'M',
        }
        defaults.update(kwargs)
        
        return Pet.objects.create(
            name=name,
            owner=owner,
            **defaults
        )
    
    @staticmethod
    def create_test_appointment(pet, vet, client, **kwargs):
        """Create a test appointment with default values"""
        from appointments.models import Appointment
        from datetime import date, time
        
        defaults = {
            'date': date.today(),
            'time': time(14, 0),
            'appointment_type': 'GENERAL',
            'status': 'SCHEDULED',
        }
        defaults.update(kwargs)
        
        return Appointment.objects.create(
            pet=pet,
            vet=vet,
            client=client,
            **defaults
        )


# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def login_user(test_case, user):
        """Helper to login a user in test cases"""
        test_case.client.login(
            username=user.username,
            password='testpass123'
        )
    
    @staticmethod
    def create_test_image():
        """Create a test image file for upload tests"""
        from PIL import Image
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=img_buffer.getvalue(),
            content_type='image/jpeg'
        )
    
    @staticmethod
    def assert_model_fields(test_case, model_instance, expected_fields):
        """Assert that a model instance has expected field values"""
        for field, expected_value in expected_fields.items():
            actual_value = getattr(model_instance, field)
            test_case.assertEqual(
                actual_value, 
                expected_value,
                f"Field '{field}' expected {expected_value}, got {actual_value}"
            )


# Mock data for tests
MOCK_DATA = {
    'users': {
        'admin': {
            'username': 'admin_test',
            'email': 'admin@test.com',
            'role': 'admin',
            'phone': '1111111111',
            'address': '123 Admin St'
        },
        'vet': {
            'username': 'vet_test', 
            'email': 'vet@test.com',
            'role': 'vet',
            'phone': '2222222222',
            'address': '123 Vet St'
        },
        'staff': {
            'username': 'staff_test',
            'email': 'staff@test.com', 
            'role': 'staff',
            'phone': '3333333333',
            'address': '123 Staff St'
        },
        'client': {
            'username': 'client_test',
            'email': 'client@test.com',
            'role': 'client', 
            'phone': '4444444444',
            'address': '123 Client St'
        }
    },
    'pets': [
        {
            'name': 'Buddy',
            'species': 'DOG',
            'breed': 'Golden Retriever',
            'age': 3,
            'gender': 'M'
        },
        {
            'name': 'Whiskers',
            'species': 'CAT', 
            'breed': 'Persian',
            'age': 2,
            'gender': 'F'
        },
        {
            'name': 'Rex',
            'species': 'DOG',
            'breed': 'German Shepherd', 
            'age': 5,
            'gender': 'M'
        }
    ],
    'inventory_items': [
        {
            'name': 'Dog Food Premium',
            'category': 'FOOD',
            'unit_price': '29.99',
            'stock_quantity': 50,
            'minimum_stock': 10
        },
        {
            'name': 'Cat Litter',
            'category': 'SUPPLY',
            'unit_price': '15.99', 
            'stock_quantity': 30,
            'minimum_stock': 5
        },
        {
            'name': 'Vaccination Kit',
            'category': 'MEDICINE',
            'unit_price': '45.00',
            'stock_quantity': 20,
            'minimum_stock': 3
        }
    ]
}


# Performance testing utilities
class PerformanceTestMixin:
    """Mixin for performance testing"""
    
    def assertMaxQueries(self, max_queries):
        """Context manager to assert maximum number of database queries"""
        from django.test.utils import override_settings
        from django.db import connection
        
        class QueryAssertion:
            def __init__(self, max_queries):
                self.max_queries = max_queries
                
            def __enter__(self):
                self.initial_queries = len(connection.queries)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    return
                final_queries = len(connection.queries)
                executed_queries = final_queries - self.initial_queries
                if executed_queries > self.max_queries:
                    raise AssertionError(
                        f"Expected maximum {self.max_queries} queries, "
                        f"but {executed_queries} were executed"
                    )
        
        return QueryAssertion(max_queries)
