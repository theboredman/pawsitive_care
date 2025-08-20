"""
Repository Pattern Implementation for Pet Data Access

Provides a clean interface for data access operations and
centralizes query logic for the Pets application.
"""

from django.db import models
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class PetQuerySet(models.QuerySet):
    def search(self, query):
        """
        Search pets by name, species, breed, or owner information
        
        Args:
            query: Search term
        Returns:
            QuerySet of matching pets
        """
        return self.filter(
            Q(name__icontains=query) |
            Q(species__icontains=query) |
            Q(breed__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query) |
            Q(owner__email__icontains=query) |
            Q(microchip_id__icontains=query)
        )

    def by_species(self, species):
        """
        Filter pets by species
        
        Args:
            species: Species code (e.g., 'DOG', 'CAT')
        Returns:
            QuerySet of pets filtered by species
        """
        return self.filter(species=species)

    def for_user(self, user):
        """
        Filter pets for specific user, considering staff status
        
        Args:
            user: User instance
        Returns:
            QuerySet of pets accessible to the user
        """
        if user.is_staff:
            return self
        return self.filter(owner=user)

    def active(self):
        """
        Return only active pets
        
        Returns:
            QuerySet of active pets
        """
        return self.filter(is_active=True)

    def with_medical_records(self):
        """Return pets with their medical records"""
        return self.prefetch_related('medical_records')

    def with_documents(self):
        """Return pets with their documents"""
        return self.prefetch_related('documents')

    def with_photos(self):
        """Return pets with their photos"""
        return self.prefetch_related('photos')