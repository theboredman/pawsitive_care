from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.http import HttpResponse
from .models import BlogPost, BlogCategory, BlogComment, BlogLike


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'post_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    
    def post_count(self, obj):
        """Count of posts in this category"""
        return obj.blogpost_set.count()
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'author_role', 'category', 'post_type', 'is_published', 
        'is_featured', 'featured_image_preview', 'views_count', 'likes_count', 'created_at'
    ]
    list_filter = [
        'is_published', 'is_professional_advice', 'is_featured',
        'category', 'author__role', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'medication_name', 'author__username', 'author__first_name', 'author__last_name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'likes_count', 'created_at', 'updated_at', 'featured_image_preview', 'media_info']
    list_editable = ['is_published', 'is_featured']
    actions = ['make_published', 'make_unpublished', 'make_featured', 'remove_featured', 'export_selected_posts']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'excerpt')
        }),
        ('Content', {
            'fields': ('content', 'featured_image', 'featured_image_preview', 'media_info')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at', 'is_featured')
        }),
        ('Medical Information', {
            'fields': (
                'is_professional_advice', 'medical_disclaimer',
                'medication_name', 'dosage_info', 'side_effects'
            ),
            'classes': ('collapse',)
        }),
        ('Pet Information', {
            'fields': ('related_pet',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def author_role(self, obj):
        """Display author's role with color coding"""
        role = obj.author.role if hasattr(obj.author, 'role') else 'client'
        colors = {
            'veterinarian': '#28a745',
            'staff': '#ffc107', 
            'admin': '#dc3545',
            'client': '#6c757d'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(role, '#6c757d'),
            role.title()
        )
    author_role.short_description = 'Role'
    
    def post_type(self, obj):
        """Display post type with badges"""
        if obj.is_professional_advice:
            if obj.medication_name:
                return format_html('<span class="badge" style="background: #17a2b8; color: white;">Medication</span>')
            else:
                return format_html('<span class="badge" style="background: #28a745; color: white;">Professional</span>')
        return format_html('<span class="badge" style="background: #6c757d; color: white;">Standard</span>')
    post_type.short_description = 'Type'
    
    def featured_image_preview(self, obj):
        """Display preview of featured image"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return format_html('<span style="color: #6c757d;">No image</span>')
    featured_image_preview.short_description = 'Image'
    
    def media_info(self, obj):
        """Display media file information"""
        if obj.featured_image:
            try:
                size_mb = obj.featured_image.size / (1024 * 1024)
                return format_html(
                    '<strong>File:</strong> {}<br>'
                    '<strong>Size:</strong> {:.2f} MB<br>'
                    '<strong>Path:</strong> {}',
                    obj.featured_image.name.split('/')[-1],
                    size_mb,
                    obj.featured_image.name
                )
            except:
                return 'File information unavailable'
        return 'No media file'
    media_info.short_description = 'Media Details'
    
    # Admin actions
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} posts published.')
    make_published.short_description = 'Publish selected posts'
    
    def make_unpublished(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} posts unpublished.')
    make_unpublished.short_description = 'Unpublish selected posts'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts marked as featured.')
    make_featured.short_description = 'Mark as featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts removed from featured.')
    remove_featured.short_description = 'Remove from featured'
    
    def export_selected_posts(self, request, queryset):
        """Export selected posts as CSV"""
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="blog_posts.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Author', 'Category', 'Published', 'Views', 'Likes', 'Created'])
        
        for post in queryset:
            writer.writerow([
                post.title,
                post.author.username,
                post.category.name if post.category else '',
                'Yes' if post.is_published else 'No',
                post.views_count,
                post.likes_count,
                post.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_selected_posts.short_description = 'Export selected posts as CSV'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category', 'related_pet').annotate(
            comments_count=Count('comments')
        )


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'post_title', 'content_preview', 
        'is_approved', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'disapprove_comments']
    
    def post_title(self, obj):
        """Get post title with link"""
        url = reverse('admin:petmedia_blogpost_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_title.short_description = 'Post'
    
    def content_preview(self, obj):
        """Show preview of comment content"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def approve_comments(self, request, queryset):
        """Approve selected comments"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def disapprove_comments(self, request, queryset):
        """Disapprove selected comments"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments disapproved.')
    disapprove_comments.short_description = 'Disapprove selected comments'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post')


@admin.register(BlogLike)
class BlogLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_title', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    readonly_fields = ['created_at']
    
    def post_title(self, obj):
        """Get post title with link"""
        url = reverse('admin:petmedia_blogpost_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_title.short_description = 'Post'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')
