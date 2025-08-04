"""
Factory Pattern Implementation for Pet Records

Provides factories for creating different types of pet-related records:
- Medical Records
- Documents
- Photos
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PetRecordFactory(ABC):
    @abstractmethod
    def create_record(self, pet, data: Dict[str, Any]):
        """
        Create a pet-related record
        
        Args:
            pet: Pet instance the record belongs to
            data: Dictionary containing record data
        Returns:
            Created record instance
        """
        pass

class MedicalRecordFactory(PetRecordFactory):
    def create_record(self, pet, data: Dict[str, Any]):
        """Create a medical record"""
        from ..models import MedicalRecord
        
        try:
            record = MedicalRecord.objects.create(
                pet=pet,
                diagnosis=data.get('diagnosis'),
                treatment=data.get('treatment'),
                notes=data.get('notes')
            )
            logger.info(f"Created medical record for pet {pet.name}")
            return record
        except Exception as e:
            logger.error(f"Failed to create medical record: {str(e)}")
            raise

class DocumentFactory(PetRecordFactory):
    def create_record(self, pet, data: Dict[str, Any]):
        """Create a pet document"""
        from ..models import PetDocument
        
        try:
            document = PetDocument.objects.create(
                pet=pet,
                title=data.get('title'),
                file=data.get('file')
            )
            logger.info(f"Created document for pet {pet.name}")
            return document
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise

class PhotoFactory(PetRecordFactory):
    def create_record(self, pet, data: Dict[str, Any]):
        """Create a pet photo"""
        from ..models import PetPhoto
        
        try:
            photo = PetPhoto.objects.create(
                pet=pet,
                image=data.get('image'),
                caption=data.get('caption')
            )
            logger.info(f"Created photo for pet {pet.name}")
            return photo
        except Exception as e:
            logger.error(f"Failed to create photo: {str(e)}")
            raise