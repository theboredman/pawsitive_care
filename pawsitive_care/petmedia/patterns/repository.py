"""
Repository Pattern for PetMedia Blog

Provides an abstraction layer for data access operations.
Centralizes query logic and makes code more maintainable and testable.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from django.db.models import Q, QuerySet
from django.core.paginator import Paginator, Page
from django.utils import timezone
import logging

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from ..models import BlogPost, BlogCategory, BlogComment, BlogLike

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Abstract base repository interface"""
    
    @abstractmethod
    def get_by_id(self, id: int):
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def get_all(self):
        """Get all entities"""
        pass
    
    @abstractmethod
    def create(self, **kwargs):
        """Create new entity"""
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs):
        """Update entity"""
        pass
    
    @abstractmethod
    def delete(self, id: int):
        """Delete entity"""
        pass


class BlogPostRepository(BaseRepository):
    """Repository for BlogPost operations"""
    
    def __init__(self):
        from ..models import BlogPost
        self.model = BlogPost
    
    def get_by_id(self, id: int) -> Optional['BlogPost']:
        """Get blog post by ID"""
        try:
            return self.model.objects.select_related('author', 'category', 'related_pet').get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet['BlogPost']:
        """Get all blog posts"""
        return self.model.objects.select_related('author', 'category', 'related_pet').all()
    
    def get_published(self) -> QuerySet['BlogPost']:
        """Get only published blog posts"""
        return self.model.objects.filter(
            is_published=True,
            published_at__lte=timezone.now()
        ).select_related('author', 'category', 'related_pet')
    
    def get_by_author(self, author: 'User') -> QuerySet['BlogPost']:
        """Get posts by specific author"""
        return self.model.objects.filter(
            author=author
        ).select_related('category', 'related_pet')
    
    def get_by_category(self, category: 'BlogCategory') -> QuerySet['BlogPost']:
        """Get posts by category"""
        return self.model.objects.filter(
            category=category,
            is_published=True
        ).select_related('author', 'related_pet')
    
    def get_professional_posts(self) -> QuerySet['BlogPost']:
        """Get professional advice posts"""
        return self.model.objects.filter(
            is_professional_advice=True,
            is_published=True
        ).select_related('author', 'category', 'related_pet')
    
    def get_medication_posts(self) -> QuerySet['BlogPost']:
        """Get medication-related posts"""
        return self.model.objects.filter(
            is_published=True
        ).exclude(
            medication_name__isnull=True
        ).exclude(
            medication_name__exact=''
        ).select_related('author', 'category', 'related_pet')
    
    def search_posts(self, query: str) -> QuerySet['BlogPost']:
        """Search posts by title, content, or medication name"""
        return self.model.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(medication_name__icontains=query) |
            Q(excerpt__icontains=query),
            is_published=True
        ).select_related('author', 'category', 'related_pet')
    
    def get_popular_posts(self, limit: int = 10) -> QuerySet['BlogPost']:
        """Get most popular posts by view count"""
        return self.model.objects.filter(
            is_published=True
        ).order_by('-views_count')[:limit].select_related('author', 'category', 'related_pet')
    
    def get_recent_posts(self, limit: int = 10) -> QuerySet['BlogPost']:
        """Get most recent posts"""
        return self.model.objects.filter(
            is_published=True
        ).order_by('-created_at')[:limit].select_related('author', 'category', 'related_pet')
    
    def get_featured_posts(self) -> QuerySet['BlogPost']:
        """Get featured posts"""
        return self.model.objects.filter(
            is_featured=True,
            is_published=True
        ).select_related('author', 'category', 'related_pet')
    
    def get_paginated_posts(self, page: int = 1, per_page: int = 10, 
                           filters: Optional[Dict[str, Any]] = None) -> Page:
        """Get paginated posts with optional filters"""
        queryset = self.get_published()
        
        if filters:
            if filters.get('category'):
                queryset = queryset.filter(category=filters['category'])
            if filters.get('author'):
                queryset = queryset.filter(author=filters['author'])
            if filters.get('is_professional'):
                queryset = queryset.filter(is_professional_advice=True)
            if filters.get('has_medication'):
                queryset = queryset.exclude(medication_name__isnull=True).exclude(medication_name__exact='')
            if filters.get('search'):
                queryset = self.search_posts(filters['search'])
        
        queryset = queryset.order_by('-created_at')
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)
    
    def create(self, **kwargs) -> 'BlogPost':
        """Create new blog post"""
        post = self.model(**kwargs)
        post.save()
        logger.info(f"Blog post created: {post.id}")
        return post
    
    def update(self, id: int, **kwargs) -> Optional['BlogPost']:
        """Update blog post"""
        try:
            post = self.model.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(post, key, value)
            post.save()
            logger.info(f"Blog post updated: {post.id}")
            return post
        except self.model.DoesNotExist:
            return None
    
    def delete(self, id: int) -> bool:
        """Delete blog post"""
        try:
            post = self.model.objects.get(id=id)
            post.delete()
            logger.info(f"Blog post deleted: {id}")
            return True
        except self.model.DoesNotExist:
            return False
    
    def increment_view_count(self, id: int) -> bool:
        """Increment view count for a post"""
        try:
            post = self.model.objects.get(id=id)
            post.views_count += 1
            post.save(update_fields=['views_count'])
            return True
        except self.model.DoesNotExist:
            return False


class BlogCategoryRepository(BaseRepository):
    """Repository for BlogCategory operations"""
    
    def __init__(self):
        from ..models import BlogCategory
        self.model = BlogCategory
    
    def get_by_id(self, id: int) -> Optional['BlogCategory']:
        """Get category by ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_by_name(self, name: str) -> Optional['BlogCategory']:
        """Get category by name"""
        try:
            return self.model.objects.get(name=name)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet['BlogCategory']:
        """Get all categories"""
        return self.model.objects.all()
    
    def get_active_categories(self) -> QuerySet['BlogCategory']:
        """Get categories that have published posts"""
        return self.model.objects.filter(
            blogpost__is_published=True
        ).distinct()
    
    def create(self, **kwargs) -> 'BlogCategory':
        """Create new category"""
        category = self.model(**kwargs)
        category.save()
        return category
    
    def update(self, id: int, **kwargs) -> Optional['BlogCategory']:
        """Update category"""
        try:
            category = self.model.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(category, key, value)
            category.save()
            return category
        except self.model.DoesNotExist:
            return None
    
    def delete(self, id: int) -> bool:
        """Delete category"""
        try:
            category = self.model.objects.get(id=id)
            category.delete()
            return True
        except self.model.DoesNotExist:
            return False


class BlogCommentRepository(BaseRepository):
    """Repository for BlogComment operations"""
    
    def __init__(self):
        from ..models import BlogComment
        self.model = BlogComment
    
    def get_by_id(self, id: int) -> Optional['BlogComment']:
        """Get comment by ID"""
        try:
            return self.model.objects.select_related('author', 'post').get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet['BlogComment']:
        """Get all comments"""
        return self.model.objects.select_related('author', 'post').all()
    
    def get_by_post(self, post_id: int) -> QuerySet['BlogComment']:
        """Get comments for a specific post"""
        return self.model.objects.filter(
            post_id=post_id,
            is_approved=True
        ).select_related('author').order_by('created_at')
    
    def get_pending_comments(self) -> QuerySet['BlogComment']:
        """Get comments pending approval"""
        return self.model.objects.filter(
            is_approved=False
        ).select_related('author', 'post')
    
    def get_by_author(self, author: 'User') -> QuerySet['BlogComment']:
        """Get comments by author"""
        return self.model.objects.filter(
            author=author
        ).select_related('post')
    
    def create(self, **kwargs) -> 'BlogComment':
        """Create new comment"""
        comment = self.model(**kwargs)
        comment.save()
        logger.info(f"Comment created: {comment.id}")
        return comment
    
    def update(self, id: int, **kwargs) -> Optional['BlogComment']:
        """Update comment"""
        try:
            comment = self.model.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(comment, key, value)
            comment.save()
            return comment
        except self.model.DoesNotExist:
            return None
    
    def delete(self, id: int) -> bool:
        """Delete comment"""
        try:
            comment = self.model.objects.get(id=id)
            comment.delete()
            logger.info(f"Comment deleted: {id}")
            return True
        except self.model.DoesNotExist:
            return False
    
    def approve_comment(self, id: int) -> bool:
        """Approve a comment"""
        try:
            comment = self.model.objects.get(id=id)
            comment.is_approved = True
            comment.save(update_fields=['is_approved'])
            logger.info(f"Comment approved: {id}")
            return True
        except self.model.DoesNotExist:
            return False


class BlogLikeRepository(BaseRepository):
    """Repository for BlogLike operations"""
    
    def __init__(self):
        from ..models import BlogLike
        self.model = BlogLike
    
    def get_by_id(self, id: int) -> Optional['BlogLike']:
        """Get like by ID"""
        try:
            return self.model.objects.select_related('user', 'post').get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet['BlogLike']:
        """Get all likes"""
        return self.model.objects.select_related('user', 'post').all()
    
    def get_by_post(self, post_id: int) -> QuerySet['BlogLike']:
        """Get likes for a specific post"""
        return self.model.objects.filter(post_id=post_id).select_related('user')
    
    def get_by_user(self, user: 'User') -> QuerySet['BlogLike']:
        """Get likes by user"""
        return self.model.objects.filter(user=user).select_related('post')
    
    def user_has_liked_post(self, user: 'User', post_id: int) -> bool:
        """Check if user has liked a specific post"""
        return self.model.objects.filter(user=user, post_id=post_id).exists()
    
    def get_post_like_count(self, post_id: int) -> int:
        """Get like count for a post"""
        return self.model.objects.filter(post_id=post_id).count()
    
    def create(self, **kwargs) -> 'BlogLike':
        """Create new like"""
        like = self.model(**kwargs)
        like.save()
        return like
    
    def update(self, id: int, **kwargs) -> Optional['BlogLike']:
        """Update like (rarely used)"""
        try:
            like = self.model.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(like, key, value)
            like.save()
            return like
        except self.model.DoesNotExist:
            return None
    
    def delete(self, id: int) -> bool:
        """Delete like"""
        try:
            like = self.model.objects.get(id=id)
            like.delete()
            return True
        except self.model.DoesNotExist:
            return False
    
    def toggle_like(self, user: 'User', post_id: int) -> tuple[bool, int]:
        """Toggle like status for user and post. Returns (is_liked, total_likes)"""
        try:
            like = self.model.objects.get(user=user, post_id=post_id)
            like.delete()
            is_liked = False
        except self.model.DoesNotExist:
            self.model.objects.create(user=user, post_id=post_id)
            is_liked = True
        
        total_likes = self.get_post_like_count(post_id)
        return is_liked, total_likes


class RepositoryManager:
    """Central manager for all repositories"""
    
    def __init__(self):
        self._post_repo = None
        self._category_repo = None
        self._comment_repo = None
        self._like_repo = None
    
    @property
    def posts(self) -> BlogPostRepository:
        """Get blog post repository"""
        if self._post_repo is None:
            self._post_repo = BlogPostRepository()
        return self._post_repo
    
    @property
    def categories(self) -> BlogCategoryRepository:
        """Get category repository"""
        if self._category_repo is None:
            self._category_repo = BlogCategoryRepository()
        return self._category_repo
    
    @property
    def comments(self) -> BlogCommentRepository:
        """Get comment repository"""
        if self._comment_repo is None:
            self._comment_repo = BlogCommentRepository()
        return self._comment_repo
    
    @property
    def likes(self) -> BlogLikeRepository:
        """Get like repository"""
        if self._like_repo is None:
            self._like_repo = BlogLikeRepository()
        return self._like_repo


# Global repository manager instance
repo_manager = RepositoryManager()
