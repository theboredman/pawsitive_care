from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator

from .models import BlogPost, BlogCategory, BlogComment, BlogLike
from .patterns.repository import repo_manager
from .patterns.factory import BlogPostFactory
from .patterns.observer import blog_event_subject
from .forms import BlogPostForm, ProfessionalBlogPostForm, MedicationBlogPostForm, CommentForm
from accounts.decorators import admin_required


class BlogListView(ListView):
    """List view for blog posts"""
    model = BlogPost
    template_name = 'petmedia/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return repo_manager.posts.get_published().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = repo_manager.categories.get_active_categories()
        context['featured_posts'] = repo_manager.posts.get_featured_posts()[:3]
        return context


class BlogDetailView(DetailView):
    """Detail view for a single blog post"""
    model = BlogPost
    template_name = 'petmedia/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return repo_manager.posts.get_published()
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        repo_manager.posts.increment_view_count(obj.id)
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Get comments
        context['comments'] = repo_manager.comments.get_by_post(post.id)
        context['comment_form'] = CommentForm()
        
        # Check if user has liked the post
        if self.request.user.is_authenticated:
            context['user_has_liked'] = repo_manager.likes.user_has_liked_post(
                self.request.user, post.id
            )
        else:
            context['user_has_liked'] = False
        
        # Get like count
        context['like_count'] = repo_manager.likes.get_post_like_count(post.id)
        
        # Related posts
        if post.category:
            context['related_posts'] = repo_manager.posts.get_by_category(post.category).exclude(id=post.id)[:3]
        
        return context


class CategoryView(ListView):
    """View for posts in a specific category"""
    template_name = 'petmedia/category.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, name=self.kwargs['name'])
        return repo_manager.posts.get_by_category(self.category)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfessionalAdviceView(ListView):
    """View for professional advice posts"""
    template_name = 'petmedia/professional_advice.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return repo_manager.posts.get_professional_posts().order_by('-created_at')


class MedicationPostsView(ListView):
    """View for medication-related posts"""
    template_name = 'petmedia/medications.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return repo_manager.posts.get_medication_posts().order_by('-created_at')


class SearchView(ListView):
    """Search view for blog posts"""
    template_name = 'petmedia/search.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return repo_manager.posts.search_posts(query)
        return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    """Create a standard blog post"""
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'petmedia/create_post.html'
    success_url = reverse_lazy('petmedia:blog_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            # Use factory pattern to create post
            post = BlogPostFactory.create_post(
                'standard',
                self.request.user,
                form.cleaned_data
            )
            
            # Trigger observer event
            blog_event_subject.post_created(post)
            
            messages.success(self.request, 'Blog post created successfully!')
            return redirect('petmedia:blog_detail', slug=post.slug)
            
        except PermissionError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class CreateProfessionalPostView(LoginRequiredMixin, CreateView):
    """Create a professional advice post"""
    model = BlogPost
    form_class = ProfessionalBlogPostForm
    template_name = 'petmedia/create_professional_post.html'
    success_url = reverse_lazy('petmedia:blog_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is a veterinarian
        if not (request.user.is_authenticated and hasattr(request.user, 'role') and request.user.is_vet()):
            messages.error(request, 'Only veterinarians can create professional advice posts.')
            return redirect('petmedia:blog_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            # Use factory pattern to create post
            post = BlogPostFactory.create_post(
                'professional',
                self.request.user,
                form.cleaned_data
            )
            
            # Trigger observer event
            blog_event_subject.post_created(post)
            
            messages.success(self.request, 'Professional blog post created successfully!')
            return redirect('petmedia:blog_detail', slug=post.slug)
            
        except PermissionError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class CreateMedicationPostView(LoginRequiredMixin, CreateView):
    """Create a medication-specific post"""
    model = BlogPost
    form_class = MedicationBlogPostForm
    template_name = 'petmedia/create_medication_post.html'
    success_url = reverse_lazy('petmedia:blog_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is a veterinarian
        if not (request.user.is_authenticated and hasattr(request.user, 'role') and request.user.is_vet()):
            messages.error(request, 'Only veterinarians can create medication posts.')
            return redirect('petmedia:blog_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            # Use factory pattern to create post
            post = BlogPostFactory.create_post(
                'medication',
                self.request.user,
                form.cleaned_data
            )
            
            # Trigger observer event
            blog_event_subject.post_created(post)
            
            messages.success(self.request, 'Medication post created successfully!')
            return redirect('petmedia:blog_detail', slug=post.slug)
            
        except PermissionError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class UserPostsView(LoginRequiredMixin, ListView):
    """View for user's own blog posts"""
    template_name = 'petmedia/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return repo_manager.posts.get_by_author(self.request.user).order_by('-created_at')


@login_required
@require_http_methods(["POST"])
def toggle_like(request, pk):
    """Toggle like status for a blog post"""
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    
    is_liked, total_likes = repo_manager.likes.toggle_like(request.user, post.id)
    
    # Trigger observer event
    if is_liked:
        blog_event_subject.post_liked(post, request.user)
    
    return JsonResponse({
        'is_liked': is_liked,
        'total_likes': total_likes
    })


@login_required
@require_http_methods(["POST"])
def add_comment(request, pk):
    """Add a comment to a blog post"""
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = repo_manager.comments.create(
            post=post,
            author=request.user,
            content=form.cleaned_data['content'],
            is_approved=True  # Auto-approve for now
        )
        
        # Trigger observer event
        blog_event_subject.comment_added(comment)
        
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Error adding comment. Please try again.')
    
    return redirect('petmedia:blog_detail', slug=post.slug)


def get_categories_ajax(request):
    """AJAX endpoint to get categories"""
    categories = repo_manager.categories.get_all()
    data = [{'id': cat.id, 'name': cat.name} for cat in categories]
    return JsonResponse({'categories': data})


# Admin Post Management Views
@admin_required
def admin_post_management(request):
    """Admin view to manage all blog posts"""
    posts_list = BlogPost.objects.select_related('author', 'category').order_by('-created_at')
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter == 'published':
        posts_list = posts_list.filter(is_published=True)
    elif status_filter == 'unpublished':
        posts_list = posts_list.filter(is_published=False)
    elif status_filter == 'featured':
        posts_list = posts_list.filter(is_featured=True)
    elif status_filter == 'professional':
        posts_list = posts_list.filter(is_professional_advice=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts_list, 20)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_posts': BlogPost.objects.count(),
        'published_posts': BlogPost.objects.filter(is_published=True).count(),
        'unpublished_posts': BlogPost.objects.filter(is_published=False).count(),
        'featured_posts': BlogPost.objects.filter(is_featured=True).count(),
        'professional_posts': BlogPost.objects.filter(is_professional_advice=True).count(),
    }
    
    context = {
        'posts': posts,
        'stats': stats,
        'current_filter': status_filter,
        'search_query': search_query,
        'page_obj': posts,
    }
    
    return render(request, 'petmedia/admin/post_management.html', context)


@admin_required
@require_http_methods(["POST"])
def admin_toggle_post_status(request, post_id):
    """Toggle post published status"""
    post = get_object_or_404(BlogPost, id=post_id)
    post.is_published = not post.is_published
    post.save()
    
    status = "published" if post.is_published else "hidden"
    messages.success(request, f'Post "{post.title}" has been {status}.')
    
    return JsonResponse({
        'success': True,
        'is_published': post.is_published,
        'status': status
    })


@admin_required
@require_http_methods(["POST"])
def admin_toggle_post_featured(request, post_id):
    """Toggle post featured status"""
    post = get_object_or_404(BlogPost, id=post_id)
    post.is_featured = not post.is_featured
    post.save()
    
    status = "featured" if post.is_featured else "removed from featured"
    messages.success(request, f'Post "{post.title}" has been {status}.')
    
    return JsonResponse({
        'success': True,
        'is_featured': post.is_featured,
        'status': status
    })


@admin_required
@require_http_methods(["POST"])
def admin_delete_post(request, post_id):
    """Delete a blog post"""
    post = get_object_or_404(BlogPost, id=post_id)
    post_title = post.title
    post.delete()
    
    messages.success(request, f'Post "{post_title}" has been permanently deleted.')
    
    return JsonResponse({
        'success': True,
        'message': f'Post "{post_title}" has been deleted.'
    })


@admin_required
def admin_post_detail(request, post_id):
    """Admin view for post details with management options"""
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.select_related('author').order_by('-created_at')
    
    context = {
        'post': post,
        'comments': comments,
        'comment_count': comments.count(),
        'likes_count': post.likes.count(),
    }
    
    return render(request, 'petmedia/admin/post_detail.html', context)
