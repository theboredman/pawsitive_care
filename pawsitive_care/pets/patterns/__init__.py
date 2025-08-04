"""
Design Patterns for the Pets Application

This package contains implementations of various design patterns:
- Observer Pattern: For notification handling
- Factory Pattern: For creating different types of pet records
- Repository Pattern: For data access abstraction
"""

from .observer import PetObserver, EmailNotifier
from .factory import MedicalRecordFactory, DocumentFactory, PhotoFactory
from .repository import PetQuerySet

__all__ = [
    'PetObserver',
    'EmailNotifier',
    'MedicalRecordFactory',
    'DocumentFactory',
    'PhotoFactory',
    'PetQuerySet'
]