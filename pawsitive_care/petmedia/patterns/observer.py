"""
Observer Pattern for PetMedia Blog

Handles notifications and events when blog posts are created, updated, or commented on.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):
    """Abstract observer interface"""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle event notification"""
        pass


class Subject(ABC):
    """Abstract subject interface"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers"""
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")


class BlogEventSubject(Subject):
    """Subject for blog-related events"""
    
    def post_created(self, post) -> None:
        """Notify when a new blog post is created"""
        self.notify('post_created', {
            'post': post,
            'author': post.author,
            'category': post.category,
            'is_professional': post.is_professional_advice
        })
    
    def post_published(self, post) -> None:
        """Notify when a blog post is published"""
        self.notify('post_published', {
            'post': post,
            'author': post.author
        })
    
    def comment_added(self, comment) -> None:
        """Notify when a comment is added"""
        self.notify('comment_added', {
            'comment': comment,
            'post': comment.post,
            'commenter': comment.author
        })
    
    def post_liked(self, post, user) -> None:
        """Notify when a post is liked"""
        self.notify('post_liked', {
            'post': post,
            'user': user,
            'author': post.author
        })


class EmailNotificationObserver(Observer):
    """Observer that sends email notifications"""
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Send email notifications based on event type"""
        try:
            if event_type == 'post_published':
                self._notify_post_published(data)
            elif event_type == 'comment_added':
                self._notify_comment_added(data)
            elif event_type == 'post_liked':
                self._notify_post_liked(data)
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _notify_post_published(self, data: Dict[str, Any]) -> None:
        """Notify when a post is published"""
        post = data['post']
        author = data['author']
        
        if author.email:
            subject = f"Your blog post '{post.title}' has been published"
            message = f"""
            Hi {author.get_full_name()},
            
            Your blog post "{post.title}" has been successfully published!
            
            View your post: {post.get_absolute_url()}
            
            Thank you for sharing your knowledge with the pet community.
            
            Best regards,
            Pawsitive Care Team
            """
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[author.email],
                fail_silently=True
            )
    
    def _notify_comment_added(self, data: Dict[str, Any]) -> None:
        """Notify when someone comments on a post"""
        comment = data['comment']
        post = data['post']
        commenter = data['commenter']
        
        # Notify post author
        if post.author.email and post.author != commenter:
            subject = f"New comment on your blog post: {post.title}"
            message = f"""
            Hi {post.author.get_full_name()},
            
            {commenter.get_full_name()} commented on your blog post "{post.title}":
            
            "{comment.content[:100]}..."
            
            View the full comment: {post.get_absolute_url()}
            
            Best regards,
            Pawsitive Care Team
            """
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[post.author.email],
                fail_silently=True
            )
    
    def _notify_post_liked(self, data: Dict[str, Any]) -> None:
        """Notify when someone likes a post"""
        post = data['post']
        user = data['user']
        author = data['author']
        
        if author.email and author != user:
            subject = f"{user.get_full_name()} liked your blog post"
            message = f"""
            Hi {author.get_full_name()},
            
            {user.get_full_name()} liked your blog post "{post.title}".
            
            View your post: {post.get_absolute_url()}
            
            Best regards,
            Pawsitive Care Team
            """
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[author.email],
                fail_silently=True
            )


class ActivityLogObserver(Observer):
    """Observer that logs activities for analytics"""
    
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log activities"""
        try:
            if event_type == 'post_created':
                self._log_post_creation(data)
            elif event_type == 'comment_added':
                self._log_comment_activity(data)
            elif event_type == 'post_liked':
                self._log_like_activity(data)
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def _log_post_creation(self, data: Dict[str, Any]) -> None:
        """Log post creation activity"""
        post = data['post']
        author = data['author']
        
        logger.info(
            f"Blog post created - ID: {post.id}, Author: {author.id}, "
            f"Category: {post.category.name if post.category else 'None'}, "
            f"Professional: {data['is_professional']}"
        )
    
    def _log_comment_activity(self, data: Dict[str, Any]) -> None:
        """Log comment activity"""
        comment = data['comment']
        
        logger.info(
            f"Comment added - Post: {comment.post.id}, "
            f"Author: {comment.author.id}"
        )
    
    def _log_like_activity(self, data: Dict[str, Any]) -> None:
        """Log like activity"""
        post = data['post']
        user = data['user']
        
        logger.info(
            f"Post liked - Post: {post.id}, User: {user.id}"
        )


# Global blog event subject
blog_event_subject = BlogEventSubject()

# Attach observers
blog_event_subject.attach(EmailNotificationObserver())
blog_event_subject.attach(ActivityLogObserver())
