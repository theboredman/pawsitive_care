from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Pet, MedicalRecord, PetDocument
from datetime import date, timedelta

class PetFeatureTests(TestCase):
    def setUp(self):
        # Create test users
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123'
        )
        
        # Create a test pet
        self.pet = Pet.objects.create(
            name='TestPet',
            species='DOG',
            breed='TestBreed',
            owner=self.regular_user
        )

    def test_pet_detail_view(self):
        """Test the pet detail view displays correctly"""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('pets:pet_detail', args=[self.pet.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestPet')
        self.assertContains(response, 'TestBreed')

    def test_add_medical_record(self):
        """Test adding a medical record"""
        self.client.login(username='staff', password='testpass123')
        
        data = {
            'date': date.today(),
            'record_type': 'checkup',
            'description': 'Test checkup',
            'next_visit_date': date.today() + timedelta(days=30)
        }
        
        response = self.client.post(
            reverse('pets:add_medical_record', args=[self.pet.pk]),
            data
        )
        
        self.assertEqual(MedicalRecord.objects.count(), 1)
        record = MedicalRecord.objects.first()
        self.assertEqual(record.record_type, 'checkup')
        self.assertEqual(record.pet, self.pet)

    def test_upload_document(self):
        """Test document upload"""
        self.client.login(username='regular', password='testpass123')
        
        # Create a test PDF file
        pdf_content = b'%PDF-1.4 test pdf content'
        pdf_file = SimpleUploadedFile('test.pdf', pdf_content, content_type='application/pdf')
        
        data = {
            'document_type': 'VACCINATION',
            'title': 'Test Document',
            'description': 'Test upload',
            'file': pdf_file
        }
        
        response = self.client.post(
            reverse('pets:upload_document', args=[self.pet.pk]),
            data
        )
        
        self.assertEqual(PetDocument.objects.count(), 1)
        document = PetDocument.objects.first()
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.pet, self.pet)

    def test_document_validation(self):
        """Test document upload validation"""
        self.client.login(username='regular', password='testpass123')
        
        # Try to upload an invalid file type
        exe_content = b'test exe content'
        exe_file = SimpleUploadedFile('test.exe', exe_content, content_type='application/x-msdownload')
        
        data = {
            'document_type': 'OTHER',
            'title': 'Invalid Document',
            'description': 'Should fail',
            'file': exe_file
        }
        
        response = self.client.post(
            reverse('pets:upload_document', args=[self.pet.pk]),
            data
        )
        
        # Should not create a document
        self.assertEqual(PetDocument.objects.count(), 0)

    def test_permissions(self):
        """Test permission restrictions"""
        # Create another user
        User = get_user_model()
        other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )
        
        # Try to access pet detail with unauthorized user
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('pets:pet_detail', args=[self.pet.pk]))
        self.assertEqual(response.status_code, 403)  # Should be forbidden
        
        # Try to add medical record as non-staff
        data = {
            'date': date.today(),
            'record_type': 'checkup',
            'description': 'Test checkup'
        }
        response = self.client.post(
            reverse('pets:add_medical_record', args=[self.pet.pk]),
            data
        )
        self.assertEqual(response.status_code, 403)  # Should be forbidden
