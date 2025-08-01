from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Pet, MedicalRecord, PetDocument, PetPhoto
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
            'record_type': 'CHECKUP',
            'description': 'Test checkup',
            'next_visit_date': date.today() + timedelta(days=30)
        }
        
        response = self.client.post(
            reverse('pets:add_medical_record', args=[self.pet.pk]),
            data
        )
        
        self.assertEqual(MedicalRecord.objects.count(), 1)
        record = MedicalRecord.objects.first()
        self.assertEqual(record.record_type, 'CHECKUP')
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
            'record_type': 'CHECKUP',
            'description': 'Test checkup'
        }
        response = self.client.post(
            reverse('pets:add_medical_record', args=[self.pet.pk]),
            data
        )
        self.assertEqual(response.status_code, 403)  # Should be forbidden

    def test_pet_update_validation(self):
        """Test pet update with various validation scenarios"""
        self.client.login(username='regular', password='testpass123')
        
        # Test valid update
        data = {
            'name': 'UpdatedPet',
            'species': 'DOG',  # Required field
            'breed': 'UpdatedBreed',
            'age': '3',
            'weight': '15.5',
            'gender': 'M',
            'color': 'Brown',
            'microchip_id': 'NEW123456',
            'medical_conditions': 'None',
            'special_notes': 'Updated notes',
            'vaccination_status': 'UP_TO_DATE'
        }
        
        response = self.client.post(
            reverse('pets:pet_update', args=[self.pet.pk]),
            data
        )
        
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, 'UpdatedPet')
        self.assertEqual(self.pet.age, 3)
        self.assertEqual(float(self.pet.weight), 15.5)
        
        # Test negative age
        data['age'] = '-1'
        response = self.client.post(
            reverse('pets:pet_update', args=[self.pet.pk]),
            data
        )
        # Pet should not be updated with negative age
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.age, 3)  # Should still be 3
        
        # Test invalid weight
        data['age'] = '4'
        data['weight'] = 'invalid'
        response = self.client.post(
            reverse('pets:pet_update', args=[self.pet.pk]),
            data
        )
        # Pet should not be updated with invalid weight
        self.pet.refresh_from_db()
        self.assertEqual(float(self.pet.weight), 15.5)  # Should still be 15.5

    def test_microchip_uniqueness(self):
        """Test microchip ID uniqueness validation"""
        # Create another pet with a microchip ID
        User = get_user_model()
        other_user = User.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        
        other_pet = Pet.objects.create(
            name='OtherPet',
            species='CAT',
            breed='Persian',
            owner=other_user,
            microchip_id='UNIQUE123'
        )
        
        self.client.login(username='regular', password='testpass123')
        
        # Try to update our pet with the same microchip ID
        data = {
            'name': 'TestPet',
            'species': 'DOG',  # Required field
            'breed': 'TestBreed',
            'gender': 'U',
            'microchip_id': 'UNIQUE123',  # Same as other pet
            'vaccination_status': 'UNKNOWN'
        }
        
        response = self.client.post(
            reverse('pets:pet_update', args=[self.pet.pk]),
            data
        )
        
        # Should not update with duplicate microchip ID
        self.pet.refresh_from_db()
        self.assertNotEqual(self.pet.microchip_id, 'UNIQUE123')

    def test_pet_photo_upload(self):
        """Test pet photo upload functionality"""
        self.client.login(username='regular', password='testpass123')
        
        # Create a test image
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        image_file = SimpleUploadedFile('test.gif', image_content, content_type='image/gif')
        
        data = {
            'image': image_file,
            'caption': 'Test photo',
            'is_primary': 'on'
        }
        
        response = self.client.post(
            reverse('pets:pet_photo_add', args=[self.pet.pk]),
            data
        )
        
        self.assertEqual(PetPhoto.objects.count(), 1)
        photo = PetPhoto.objects.first()
        self.assertEqual(photo.caption, 'Test photo')
        self.assertTrue(photo.is_primary)
        self.assertEqual(photo.pet, self.pet)
