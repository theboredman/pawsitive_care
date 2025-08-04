"""
Observer Pattern Implementation for Pet Events

Handles notifications for pet-related events such as:
- Medical record updates
- Document uploads
- Status changes
- Photo uploads
"""

from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PetObserver(ABC):
    @abstractmethod
    def update(self, pet, event_type):
        """
        Update method that gets called when a pet event occurs
        
        Args:
            pet: The pet instance that was updated
            event_type: Type of event that occurred
        """
        pass

class EmailNotifier(PetObserver):
    def update(self, pet, event_type):
        """
        Send email notification about pet updates
        
        Args:
            pet: The pet instance that was updated
            event_type: Type of event that occurred
        """
        subject = f'Pet Update: {event_type}'
        message = self._create_message(pet, event_type)
        if pet.owner.email:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [pet.owner.email],
                    fail_silently=False,
                )
                logger.info(f"Email notification sent to {pet.owner.email} for {event_type}")
            except Exception as e:
                logger.error(f"Failed to send email notification: {str(e)}")

    def _create_message(self, pet, event_type):
        """Create appropriate message based on event type"""
        messages = {
            'medical_update': f"A medical record has been updated for {pet.name}",
            'document_upload': f"A new document has been uploaded for {pet.name}",
            'photo_upload': f"A new photo has been added for {pet.name}",
            'status_change': f"Status has been updated for {pet.name}"
        }
        return messages.get(event_type, f"Update for your pet {pet.name}: {event_type}")