"""
Factory Pattern for PetMedia Blog

Creates different types of blog posts with appropriate configurations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from ..models import BlogPost

logger = logging.getLogger(__name__)


class BlogPostCreator(ABC):
    """Abstract factory for creating blog posts"""
    
    @abstractmethod
    def create_post(self, user: 'User', data: Dict[str, Any]) -> 'BlogPost':
        """Create a blog post"""
        pass
    
    @abstractmethod
    def validate_user_permissions(self, user: 'User') -> bool:
        """Validate if user can create this type of post"""
        pass
    
    def get_default_data(self) -> Dict[str, Any]:
        """Get default data for this post type"""
        return {}


class StandardBlogPostCreator(BlogPostCreator):
    """Creator for standard blog posts from pet owners"""
    
    def create_post(self, user: 'User', data: Dict[str, Any]) -> 'BlogPost':
        """Create a standard blog post"""
        from ..models import BlogPost
        
        if not self.validate_user_permissions(user):
            raise PermissionError("User not authorized to create blog posts")
        
        # Merge with defaults
        post_data = {**self.get_default_data(), **data}
        
        post = BlogPost(
            title=post_data['title'],
            content=post_data['content'],
            excerpt=post_data.get('excerpt', post_data['content'][:300]),
            author=user,
            category=post_data.get('category'),
            related_pet=post_data.get('related_pet'),
            is_professional_advice=False,
            is_published=post_data.get('is_published', True),
            slug=post_data.get('slug', ''),
            meta_description=post_data.get('meta_description', ''),
            featured_image=post_data.get('featured_image')
        )
        
        post.save()
        logger.info(f"Standard blog post created: {post.id} by user {user.id}")
        return post
    
    def validate_user_permissions(self, user: 'User') -> bool:
        """All authenticated users can create standard posts"""
        return user.is_authenticated
    
    def get_default_data(self) -> Dict[str, Any]:
        """Default data for standard posts"""
        return {
            'is_professional_advice': False,
            'is_published': True  # Auto-publish posts
        }


class ProfessionalBlogPostCreator(BlogPostCreator):
    """Creator for professional/medical blog posts from veterinarians"""
    
    def create_post(self, user: 'User', data: Dict[str, Any]) -> 'BlogPost':
        """Create a professional blog post"""
        from ..models import BlogPost
        
        if not self.validate_user_permissions(user):
            raise PermissionError("User not authorized to create professional posts")
        
        # Merge with defaults
        post_data = {**self.get_default_data(), **data}
        
        post = BlogPost(
            title=post_data['title'],
            content=post_data['content'],
            excerpt=post_data.get('excerpt', post_data['content'][:300]),
            author=user,
            category=post_data.get('category'),
            related_pet=post_data.get('related_pet'),
            is_professional_advice=True,
            is_published=post_data.get('is_published', True),
            medical_disclaimer=post_data.get('medical_disclaimer', self._get_default_disclaimer()),
            medication_name=post_data.get('medication_name', ''),
            dosage_info=post_data.get('dosage_info', ''),
            side_effects=post_data.get('side_effects', ''),
            slug=post_data.get('slug', ''),
            meta_description=post_data.get('meta_description', ''),
            featured_image=post_data.get('featured_image')
        )
        
        post.save()
        logger.info(f"Professional blog post created: {post.id} by user {user.id}")
        return post
    
    def validate_user_permissions(self, user: 'User') -> bool:
        """Only veterinarians can create professional posts"""
        return (user.is_authenticated and 
                hasattr(user, 'role') and 
                user.is_vet())
    
    def get_default_data(self) -> Dict[str, Any]:
        """Default data for professional posts"""
        return {
            'is_professional_advice': True,
            'is_published': True  # Auto-publish posts
        }
    
    def _get_default_disclaimer(self) -> str:
        """Get default medical disclaimer"""
        return (
            "This information is provided for educational purposes only and "
            "should not replace professional veterinary consultation. Always "
            "consult with a qualified veterinarian before making decisions "
            "about your pet's health or medication."
        )


class MedicationBlogPostCreator(ProfessionalBlogPostCreator):
    """Creator specifically for medication-related blog posts"""
    
    def create_post(self, user: 'User', data: Dict[str, Any]) -> 'BlogPost':
        """Create a medication blog post"""
        # Ensure medication name is provided
        if not data.get('medication_name'):
            raise ValueError("Medication name is required for medication posts")
        
        # Set category to MEDICATION if not specified
        if not data.get('category'):
            from ..models import BlogCategory
            try:
                medication_category = BlogCategory.objects.get(name='MEDICATION')
                data['category'] = medication_category
            except BlogCategory.DoesNotExist:
                pass
        
        return super().create_post(user, data)
    
    def get_default_data(self) -> Dict[str, Any]:
        """Default data for medication posts"""
        base_data = super().get_default_data()
        base_data.update({
            'medical_disclaimer': (
                "This medication information is for educational purposes only. "
                "Always follow your veterinarian's specific instructions for "
                "dosage, administration, and monitoring. Never start, stop, or "
                "change medication without veterinary supervision."
            )
        })
        return base_data


class BlogPostFactory:
    """Factory for creating different types of blog posts"""
    
    _creators = {
        'standard': StandardBlogPostCreator,
        'professional': ProfessionalBlogPostCreator,
        'medication': MedicationBlogPostCreator,
    }
    
    @classmethod
    def create_post(cls, post_type: str, user: 'User', data: Dict[str, Any]) -> 'BlogPost':
        """Create a blog post of the specified type"""
        if post_type not in cls._creators:
            raise ValueError(f"Unsupported post type: {post_type}")
        
        creator = cls._creators[post_type]()
        
        if not creator.validate_user_permissions(user):
            raise PermissionError(f"User {user.id} cannot create {post_type} posts")
        
        return creator.create_post(user, data)
    
    @classmethod
    def get_available_types(cls) -> list:
        """Get list of available post types"""
        return list(cls._creators.keys())
    
    @classmethod
    def can_user_create_type(cls, user: 'User', post_type: str) -> bool:
        """Check if user can create a specific post type"""
        if post_type not in cls._creators:
            return False
        
        creator = cls._creators[post_type]()
        return creator.validate_user_permissions(user)


# Convenience function
def create_blog_post(post_type: str, user: 'User', data: Dict[str, Any]) -> 'BlogPost':
    """Convenience function to create a blog post"""
    return BlogPostFactory.create_post(post_type, user, data)
