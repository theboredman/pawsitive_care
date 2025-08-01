"""
PetMedia Blog Models

Models for a blog platform where pet owners and veterinarians can share:
- Medication information and tips
- Pet care advice
- Health tips and experiences
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
from pets.models import Pet
import uuid

User = get_user_model()


class BlogCategory(models.Model):
    """Categories for blog posts"""
    MEDICATION = 'MEDICATION'
    HEALTH_TIPS = 'HEALTH_TIPS'
    NUTRITION = 'NUTRITION'
    TRAINING = 'TRAINING'
    GROOMING = 'GROOMING'
    EMERGENCY = 'EMERGENCY'
    EXPERIENCE = 'EXPERIENCE'
    
    CATEGORY_CHOICES = [
        (MEDICATION, 'Medications & Treatments'),
        (HEALTH_TIPS, 'Health Tips'),
        (NUTRITION, 'Nutrition & Diet'),
        (TRAINING, 'Training & Behavior'),
        (GROOMING, 'Grooming & Care'),
        (EMERGENCY, 'Emergency Care'),
        (EXPERIENCE, 'Owner Experiences'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()
    
    @property
    def slug(self):
        """Generate slug from name for URL compatibility"""
        return self.name.lower()
    
    class Meta:
        verbose_name_plural = "Blog Categories"


class BlogPost(models.Model):
    """Main blog post model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200, 
        validators=[MinLengthValidator(5)],
        help_text="Blog post title"
    )
    content = models.TextField(
        validators=[MinLengthValidator(50)],
        help_text="Full blog post content"
    )
    excerpt = models.TextField(
        max_length=300,
        help_text="Short excerpt for previews"
    )
    
    # Author and categorization
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True)
    related_pet = models.ForeignKey(
        Pet, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Pet this post is about (optional)"
    )
    
    # Medical/Professional fields
    is_professional_advice = models.BooleanField(
        default=False,
        help_text="Is this professional veterinary advice?"
    )
    medical_disclaimer = models.TextField(
        blank=True,
        help_text="Medical disclaimer for professional posts"
    )
    
    # Medication specific fields
    medication_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Name of medication discussed"
    )
    dosage_info = models.TextField(
        blank=True,
        help_text="Dosage information (for reference only)"
    )
    side_effects = models.TextField(
        blank=True,
        help_text="Known side effects"
    )
    
    # SEO and metadata
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    featured_image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True
    )
    
    # Status and engagement
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Auto-publish posts and set published_at timestamp
        if not self.pk:  # New post
            self.is_published = True
            self.published_at = timezone.now()
        elif self.is_published and not self.published_at:
            # If manually setting is_published to True, set published_at
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('petmedia:post_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class BlogComment(models.Model):
    """Comments on blog posts"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(validators=[MinLengthValidator(3)])
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.post.title}"
    
    class Meta:
        ordering = ['created_at']


class BlogLike(models.Model):
    """Likes for blog posts"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
