from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .models import BlogPost, BlogComment, BlogCategory
from pets.models import Pet


class CustomImageWidget(forms.ClearableFileInput):
    """Custom widget for image uploads with preview"""
    template_name = 'petmedia/widgets/image_upload.html'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control', 'accept': 'image/*'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class BlogPostForm(forms.ModelForm):
    """Form for creating standard blog posts"""
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'category', 
            'related_pet', 'featured_image', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your blog post content here...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of your post (optional)'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'related_pet': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'SEO description (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter pets to only show user's pets
        if user:
            self.fields['related_pet'].queryset = Pet.objects.filter(
                owner=user
            )
        else:
            self.fields['related_pet'].queryset = Pet.objects.none()
        
        # Make some fields optional
        self.fields['excerpt'].required = False
        self.fields['related_pet'].required = False
        self.fields['featured_image'].required = False
        self.fields['meta_description'].required = False
    
    def clean_featured_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('featured_image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large. Maximum size is 5MB.')
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError('Please upload a valid image file.')
        
        return image
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-generate slug if not provided
        if not instance.slug:
            instance.slug = slugify(instance.title)
        
        # Auto-generate excerpt if not provided
        if not instance.excerpt and instance.content:
            instance.excerpt = instance.content[:300] + '...' if len(instance.content) > 300 else instance.content
        
        if commit:
            instance.save()
        return instance


class ProfessionalBlogPostForm(BlogPostForm):
    """Form for creating professional advice posts"""
    
    class Meta(BlogPostForm.Meta):
        fields = BlogPostForm.Meta.fields + [
            'medical_disclaimer', 'medication_name', 'dosage_info', 'side_effects'
        ]
        widgets = {
            **BlogPostForm.Meta.widgets,
            'medical_disclaimer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Medical disclaimer (will use default if empty)'
            }),
            'medication_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medication name (if applicable)'
            }),
            'dosage_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dosage information (if applicable)'
            }),
            'side_effects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Known side effects (if applicable)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make medical fields optional
        self.fields['medical_disclaimer'].required = False
        self.fields['medication_name'].required = False
        self.fields['dosage_info'].required = False
        self.fields['side_effects'].required = False


class MedicationBlogPostForm(ProfessionalBlogPostForm):
    """Form for creating medication-specific posts"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make medication name required for medication posts
        self.fields['medication_name'].required = True
        self.fields['medication_name'].widget.attrs['placeholder'] = 'Medication name (required)'
    
    def clean_medication_name(self):
        """Ensure medication name is provided"""
        medication_name = self.cleaned_data.get('medication_name')
        if not medication_name or not medication_name.strip():
            raise forms.ValidationError('Medication name is required for medication posts.')
        return medication_name.strip()


class CommentForm(forms.ModelForm):
    """Form for adding comments to blog posts"""
    
    class Meta:
        model = BlogComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts...',
                'maxlength': '1000'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = 'Your Comment'


class BlogCategoryForm(forms.ModelForm):
    """Form for creating/editing blog categories"""
    
    class Meta:
        model = BlogCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description'
            })
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-generate slug if not provided
        if not instance.slug:
            instance.slug = slugify(instance.name)
        
        if commit:
            instance.save()
        return instance


class SearchForm(forms.Form):
    """Form for searching blog posts"""
    
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts, medications, tips...',
            'autocomplete': 'off'
        }),
        label='Search'
    )
    
    category = forms.ModelChoiceField(
        queryset=BlogCategory.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    professional_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Professional advice only'
    )
    
    medication_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Medication posts only'
    )
