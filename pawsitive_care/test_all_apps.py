"""
Comprehensive Test Suite for All Apps in Pawsitive Care
This file contains tests for all major functionality across all apps:
- accounts (user management and authentication)
- pets (pet management and medical records)
- appointments (appointment scheduling and management)
- billing (billing and payment processing)
- inventory (inventory management and stock tracking)
- petmedia (blog posts and media management)
- communication (messaging system)
- records (medical records management)
"""

import os
import tempfile
from datetime import date, timedelta, datetime, time
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone

# Import models from all apps
from accounts.models import CustomUser
from pets.models import Pet, MedicalRecord, PetDocument, PetPhoto
from appointments.models import Appointment, AppointmentType
from billing.models import Billing, ServiceCost
from inventory.models import InventoryItem, StockMovement, Supplier, PurchaseOrder
from petmedia.models import BlogPost, BlogCategory, BlogComment
from communication.models import *  # Import communication models if they exist
from records.models import *  # Import records models if they exist

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup for all app tests"""
    
    def setUp(self):
        """Set up test data common to all tests"""
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            phone='1234567890',
            address='123 Admin St',
            role='admin',
            first_name='Admin',
            last_name='User'
        )
        
        self.vet_user = User.objects.create_user(
            username='vet_test',
            email='vet@test.com',
            password='testpass123',
            phone='1234567891',
            address='123 Vet St',
            role='vet',
            first_name='Dr. Vet',
            last_name='Veterinarian'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='testpass123',
            phone='1234567892',
            address='123 Staff St',
            role='staff',
            first_name='Staff',
            last_name='Member'
        )
        
        self.client_user = User.objects.create_user(
            username='client_test',
            email='client@test.com',
            password='testpass123',
            phone='1234567893',
            address='123 Client St',
            role='client',
            first_name='Client',
            last_name='Owner'
        )
        
        # Create test client for HTTP requests
        self.test_client = Client()


class AccountsAppTests(BaseTestCase):
    """Test cases for the accounts app"""
    
    def test_custom_user_model(self):
        """Test CustomUser model functionality"""
        # Test user creation
        user = self.client_user
        self.assertEqual(user.username, 'client_test')
        self.assertEqual(user.role, 'client')
        self.assertTrue(user.is_client())
        self.assertFalse(user.is_admin())
        
        # Test admin user
        admin = self.admin_user
        self.assertTrue(admin.is_admin())
        self.assertFalse(admin.is_client())
        
        # Test vet user
        vet = self.vet_user
        self.assertTrue(vet.is_vet())
        self.assertFalse(vet.is_client())
        
    def test_user_registration(self):
        """Test user registration view"""
        response = self.test_client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        
        # Test user registration
        user_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'phone': '1234567894',
            'address': '123 New User St',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.test_client.post(reverse('accounts:register'), user_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        
        # Verify user was created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@test.com')
        self.assertEqual(new_user.role, 'client')  # Default role
        
    def test_user_login(self):
        """Test user login functionality"""
        # Test login page
        response = self.test_client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        
        # Test successful login
        login_data = {
            'username': 'client_test',
            'password': 'testpass123'
        }
        response = self.test_client.post(reverse('accounts:login'), login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
    def test_role_based_dashboards(self):
        """Test role-based dashboard access"""
        # Test admin dashboard
        self.test_client.login(username='admin_test', password='testpass123')
        response = self.test_client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test vet dashboard
        self.test_client.login(username='vet_test', password='testpass123')
        response = self.test_client.get(reverse('accounts:vet_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test client dashboard
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('accounts:client_dashboard'))
        self.assertEqual(response.status_code, 200)


class PetsAppTests(BaseTestCase):
    """Test cases for the pets app"""
    
    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(
            name='Buddy',
            species='DOG',
            breed='Golden Retriever',
            age=3,
            gender='M',
            weight=Decimal('25.50'),
            color='Golden',
            owner=self.client_user,
            medical_conditions='None'
        )
        
    def test_pet_model(self):
        """Test Pet model functionality"""
        self.assertEqual(self.pet.name, 'Buddy')
        self.assertEqual(self.pet.species, 'DOG')
        self.assertEqual(self.pet.owner, self.client_user)
        self.assertEqual(str(self.pet), 'Buddy (Dog)')
        
    def test_pet_creation_validation(self):
        """Test pet creation with validation"""
        # Test invalid species
        with self.assertRaises(ValidationError):
            invalid_pet = Pet(
                name='Invalid Pet',
                species='INVALID',  # Invalid choice
                owner=self.client_user
            )
            invalid_pet.full_clean()
            
    def test_pet_list_view(self):
        """Test pet list view"""
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('pets:pet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buddy')
        
    def test_pet_detail_view(self):
        """Test pet detail view"""
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('pets:pet_detail', kwargs={'pk': self.pet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buddy')
        
    def test_medical_record_creation(self):
        """Test medical record creation"""
        medical_record = MedicalRecord.objects.create(
            pet=self.pet,
            vet=self.vet_user,
            visit_date=date.today(),
            diagnosis='Healthy checkup',
            treatment='Vaccination',
            notes='Pet is in good health'
        )
        self.assertEqual(medical_record.pet, self.pet)
        self.assertEqual(medical_record.vet, self.vet_user)


class AppointmentsAppTests(BaseTestCase):
    """Test cases for the appointments app"""
    
    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(
            name='Buddy',
            species='DOG',
            breed='Golden Retriever',
            owner=self.client_user
        )
        
        self.appointment_type = AppointmentType.objects.create(
            name='General Checkup',
            description='Regular health checkup',
            base_cost=Decimal('50.00')
        )
        
        self.appointment = Appointment.objects.create(
            pet=self.pet,
            vet=self.vet_user,
            client=self.client_user,
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            appointment_type='GENERAL',
            notes='Regular checkup'
        )
        
    def test_appointment_model(self):
        """Test Appointment model functionality"""
        self.assertEqual(self.appointment.pet, self.pet)
        self.assertEqual(self.appointment.vet, self.vet_user)
        self.assertEqual(self.appointment.client, self.client_user)
        self.assertEqual(self.appointment.status, 'SCHEDULED')
        
    def test_appointment_booking(self):
        """Test appointment booking by client"""
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('appointments:book_appointment'))
        self.assertEqual(response.status_code, 200)
        
    def test_vet_schedule_view(self):
        """Test vet schedule view"""
        self.test_client.login(username='vet_test', password='testpass123')
        response = self.test_client.get(reverse('appointments:vet_schedule'))
        self.assertEqual(response.status_code, 200)
        
    def test_appointment_status_update(self):
        """Test appointment status update"""
        self.appointment.status = 'COMPLETED'
        self.appointment.save()
        self.assertEqual(self.appointment.status, 'COMPLETED')


class BillingAppTests(BaseTestCase):
    """Test cases for the billing app"""
    
    def setUp(self):
        super().setUp()
        self.pet = Pet.objects.create(
            name='Buddy',
            species='DOG',
            owner=self.client_user
        )
        
        self.appointment = Appointment.objects.create(
            pet=self.pet,
            vet=self.vet_user,
            client=self.client_user,
            date=date.today(),
            time=time(14, 0),
            appointment_type='GENERAL'
        )
        
        self.service_cost = ServiceCost.objects.create(
            service_type='GENERAL',
            cost=Decimal('50.00')
        )
        
        self.billing = Billing.objects.create(
            appointment=self.appointment,
            pet=self.pet,
            owner=self.client_user,
            service=self.service_cost,
            amount=Decimal('50.00'),
            status='pending'
        )
        
    def test_billing_model(self):
        """Test Billing model functionality"""
        self.assertEqual(self.billing.appointment, self.appointment)
        self.assertEqual(self.billing.amount, Decimal('50.00'))
        self.assertEqual(self.billing.status, 'pending')
        
    def test_service_cost_model(self):
        """Test ServiceCost model"""
        self.assertEqual(self.service_cost.service_type, 'GENERAL')
        self.assertEqual(self.service_cost.cost, Decimal('50.00'))
        
    def test_billing_status_update(self):
        """Test billing status update"""
        self.billing.status = 'paid'
        self.billing.paid_at = timezone.now()
        self.billing.save()
        self.assertEqual(self.billing.status, 'paid')
        self.assertIsNotNone(self.billing.paid_at)


class InventoryAppTests(BaseTestCase):
    """Test cases for the inventory app"""
    
    def setUp(self):
        super().setUp()
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_email='supplier@test.com',
            contact_phone='1234567890',
            address='123 Supplier St'
        )
        
        self.inventory_item = InventoryItem.objects.create(
            name='Dog Food',
            description='Premium dog food',
            category='FOOD',
            unit_price=Decimal('25.99'),
            stock_quantity=100,
            minimum_stock=10,
            supplier=self.supplier
        )
        
    def test_inventory_item_model(self):
        """Test InventoryItem model functionality"""
        self.assertEqual(self.inventory_item.name, 'Dog Food')
        self.assertEqual(self.inventory_item.category, 'FOOD')
        self.assertEqual(self.inventory_item.stock_quantity, 100)
        self.assertFalse(self.inventory_item.is_low_stock())
        
    def test_low_stock_detection(self):
        """Test low stock detection"""
        self.inventory_item.stock_quantity = 5
        self.inventory_item.save()
        self.assertTrue(self.inventory_item.is_low_stock())
        
    def test_stock_movement(self):
        """Test stock movement tracking"""
        initial_stock = self.inventory_item.stock_quantity
        movement = StockMovement.objects.create(
            item=self.inventory_item,
            movement_type='OUT',
            quantity=10,
            reason='Sale',
            performed_by=self.staff_user
        )
        
        # Refresh from database
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.stock_quantity, initial_stock - 10)
        
    def test_inventory_dashboard_view(self):
        """Test inventory dashboard access"""
        self.test_client.login(username='staff_test', password='testpass123')
        response = self.test_client.get(reverse('inventory:dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_supplier_model(self):
        """Test Supplier model"""
        self.assertEqual(self.supplier.name, 'Test Supplier')
        self.assertEqual(self.supplier.contact_email, 'supplier@test.com')


class PetMediaAppTests(BaseTestCase):
    """Test cases for the petmedia app"""
    
    def setUp(self):
        super().setUp()
        self.category = BlogCategory.objects.create(
            name='Pet Care',
            description='Tips for pet care'
        )
        
        self.blog_post = BlogPost.objects.create(
            title='How to Care for Your Dog',
            content='This is a comprehensive guide...',
            author=self.vet_user,
            category=self.category,
            is_published=True,
            blog_type='GENERAL'
        )
        
    def test_blog_post_model(self):
        """Test BlogPost model functionality"""
        self.assertEqual(self.blog_post.title, 'How to Care for Your Dog')
        self.assertEqual(self.blog_post.author, self.vet_user)
        self.assertTrue(self.blog_post.is_published)
        
    def test_blog_category_model(self):
        """Test BlogCategory model"""
        self.assertEqual(self.category.name, 'Pet Care')
        
    def test_blog_list_view(self):
        """Test blog list view"""
        response = self.test_client.get(reverse('petmedia:blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'How to Care for Your Dog')
        
    def test_blog_detail_view(self):
        """Test blog detail view"""
        response = self.test_client.get(reverse('petmedia:blog_detail', kwargs={'pk': self.blog_post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'How to Care for Your Dog')
        
    def test_blog_comment_creation(self):
        """Test blog comment functionality"""
        comment = BlogComment.objects.create(
            post=self.blog_post,
            author=self.client_user,
            content='Great article!',
            is_approved=True
        )
        self.assertEqual(comment.post, self.blog_post)
        self.assertEqual(comment.author, self.client_user)


class IntegrationTests(BaseTestCase):
    """Integration tests for cross-app functionality"""
    
    def setUp(self):
        super().setUp()
        # Set up complex scenario with multiple related objects
        self.pet = Pet.objects.create(
            name='Integration Test Pet',
            species='DOG',
            owner=self.client_user
        )
        
        self.appointment = Appointment.objects.create(
            pet=self.pet,
            vet=self.vet_user,
            client=self.client_user,
            date=date.today(),
            time=time(14, 0),
            appointment_type='GENERAL'
        )
        
        self.service_cost = ServiceCost.objects.create(
            service_type='GENERAL',
            cost=Decimal('75.00')
        )
        
        self.billing = Billing.objects.create(
            appointment=self.appointment,
            pet=self.pet,
            owner=self.client_user,
            service=self.service_cost,
            amount=Decimal('75.00')
        )
        
    def test_appointment_to_billing_workflow(self):
        """Test complete workflow from appointment to billing"""
        # Check that appointment exists
        self.assertTrue(Appointment.objects.filter(pk=self.appointment.pk).exists())
        
        # Check that billing is linked to appointment
        self.assertEqual(self.billing.appointment, self.appointment)
        self.assertEqual(self.billing.pet, self.pet)
        self.assertEqual(self.billing.owner, self.client_user)
        
        # Update appointment status
        self.appointment.status = 'COMPLETED'
        self.appointment.save()
        
        # Update billing status
        self.billing.status = 'paid'
        self.billing.paid_at = timezone.now()
        self.billing.save()
        
        # Verify the complete workflow
        self.assertEqual(self.appointment.status, 'COMPLETED')
        self.assertEqual(self.billing.status, 'paid')
        
    def test_pet_medical_history_integration(self):
        """Test pet medical history with appointments and records"""
        # Create medical record linked to appointment
        medical_record = MedicalRecord.objects.create(
            pet=self.pet,
            vet=self.vet_user,
            visit_date=self.appointment.date,
            diagnosis='Healthy',
            treatment='Vaccination',
            notes='Annual checkup completed'
        )
        
        # Verify relationships
        self.assertEqual(medical_record.pet, self.pet)
        self.assertEqual(medical_record.vet, self.appointment.vet)
        self.assertEqual(medical_record.visit_date, self.appointment.date)
        
    def test_user_permissions_across_apps(self):
        """Test user permissions across different apps"""
        # Test admin access
        self.test_client.login(username='admin_test', password='testpass123')
        response = self.test_client.get(reverse('inventory:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test client access limitations
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('pets:pet_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test vet access
        self.test_client.login(username='vet_test', password='testpass123')
        response = self.test_client.get(reverse('appointments:vet_schedule'))
        self.assertEqual(response.status_code, 200)


class DatabaseIntegrityTests(BaseTestCase):
    """Test database integrity and constraints"""
    
    def test_cascade_deletions(self):
        """Test cascade deletion behavior"""
        # Create related objects
        pet = Pet.objects.create(
            name='Test Pet',
            species='DOG',
            owner=self.client_user
        )
        
        appointment = Appointment.objects.create(
            pet=pet,
            vet=self.vet_user,
            client=self.client_user,
            date=date.today(),
            time=time(10, 0)
        )
        
        # Delete pet and verify appointment is also deleted
        pet_id = pet.id
        appointment_id = appointment.id
        pet.delete()
        
        self.assertFalse(Pet.objects.filter(id=pet_id).exists())
        self.assertFalse(Appointment.objects.filter(id=appointment_id).exists())
        
    def test_unique_constraints(self):
        """Test unique constraints"""
        # Test unique microchip ID
        pet1 = Pet.objects.create(
            name='Pet 1',
            species='DOG',
            microchip_id='CHIP123',
            owner=self.client_user
        )
        
        # Try to create another pet with same microchip ID
        with self.assertRaises(Exception):  # Should raise IntegrityError
            pet2 = Pet.objects.create(
                name='Pet 2',
                species='CAT',
                microchip_id='CHIP123',  # Duplicate
                owner=self.client_user
            )


class PerformanceTests(BaseTestCase):
    """Performance-related tests"""
    
    def test_query_optimization(self):
        """Test query optimization with select_related and prefetch_related"""
        # Create multiple related objects
        pets = []
        for i in range(10):
            pet = Pet.objects.create(
                name=f'Pet {i}',
                species='DOG',
                owner=self.client_user
            )
            pets.append(pet)
            
            Appointment.objects.create(
                pet=pet,
                vet=self.vet_user,
                client=self.client_user,
                date=date.today(),
                time=time(10, 0)
            )
        
        # Test optimized query
        with self.assertNumQueries(1):
            appointments = list(
                Appointment.objects.select_related('pet', 'vet', 'client')
                .filter(client=self.client_user)
            )
            
        self.assertEqual(len(appointments), 10)


class SecurityTests(BaseTestCase):
    """Security-related tests"""
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected views"""
        # Try to access admin dashboard without login
        response = self.test_client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try to access vet dashboard as client
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('accounts:vet_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        
    def test_object_ownership_protection(self):
        """Test that users can only access their own objects"""
        # Create another client and pet
        other_client = User.objects.create_user(
            username='other_client',
            email='other@test.com',
            password='testpass123',
            phone='1234567899',
            address='123 Other St',
            role='client'
        )
        
        other_pet = Pet.objects.create(
            name='Other Pet',
            species='CAT',
            owner=other_client
        )
        
        # Login as original client and try to access other's pet
        self.test_client.login(username='client_test', password='testpass123')
        response = self.test_client.get(reverse('pets:pet_detail', kwargs={'pk': other_pet.pk}))
        # Should be forbidden or not found (depending on implementation)
        self.assertIn(response.status_code, [403, 404])


# Test runner utility functions
def run_all_tests():
    """Utility function to run all tests"""
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['test_all_apps'])
    return failures


if __name__ == '__main__':
    # If run directly, execute all tests
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawsitive_care.settings')
    django.setup()
    
    failures = run_all_tests()
    if failures:
        exit(1)
    else:
        print("All tests passed!")
