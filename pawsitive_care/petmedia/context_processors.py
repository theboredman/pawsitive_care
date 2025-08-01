"""
Context processors for PetMedia
"""
from .patterns.repository import repo_manager


def recent_blog_posts(request):
    """Add recent blog posts to context"""
    try:
        recent_posts = repo_manager.posts.get_recent_posts(limit=3)
        return {'recent_blog_posts': recent_posts}
    except Exception:
        return {'recent_blog_posts': []}


def blog_stats(request):
    """Add blog statistics to context"""
    try:
        if request.user.is_authenticated:
            user_posts_count = repo_manager.posts.get_by_author(request.user).count()
            return {'user_blog_posts_count': user_posts_count}
        return {'user_blog_posts_count': 0}
    except Exception:
        return {'user_blog_posts_count': 0}
