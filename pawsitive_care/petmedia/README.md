# PetMedia Blog App

A Django blog application for pet owners and veterinarians to share medication information, health tips, and pet care experiences.

## Features

### Core Functionality
- **Blog Posts**: Create and share pet-related content
- **Categories**: Organized content by topics (Medications, Health Tips, Nutrition, etc.)
- **Professional Advice**: Veterinarians can post professional medical advice
- **Medication Guides**: Detailed medication information with dosage and side effects
- **Comments & Likes**: Interactive engagement features
- **Search**: Find posts by content, medication names, or keywords

### User Types
- **Pet Owners**: Can create standard blog posts about their experiences
- **Veterinarians**: Can create professional advice and medication posts
- **All Users**: Can comment, like, and engage with content

## Design Patterns Implemented

### 1. Observer Pattern (`patterns/observer.py`)
**Purpose**: Event handling and notifications for blog activities

**Components**:
- `BlogEventSubject`: Central event dispatcher
- `EmailNotificationObserver`: Sends email notifications
- `ActivityLogObserver`: Logs blog activities

**Events**:
- Post created/published
- Comments added
- Posts liked
- Professional advice posted

**Usage**:
```python
from petmedia.patterns.observer import blog_event_subject

# Trigger event when post is created
blog_event_subject.notify_observers('post_created', post)
```

### 2. Factory Pattern (`patterns/factory.py`)
**Purpose**: Creates different types of blog posts with appropriate configurations

**Components**:
- `StandardBlogPostCreator`: For regular pet owners
- `ProfessionalBlogPostCreator`: For veterinarians
- `MedicationBlogPostCreator`: For medication-specific posts
- `BlogPostFactory`: Central factory manager

**Usage**:
```python
from petmedia.patterns.factory import BlogPostFactory

# Create different post types
standard_post = BlogPostFactory.create_post('standard', user, data)
professional_post = BlogPostFactory.create_post('professional', vet_user, data)
medication_post = BlogPostFactory.create_post('medication', vet_user, data)
```

### 3. Repository Pattern (`patterns/repository.py`)
**Purpose**: Abstraction layer for data access operations

**Components**:
- `BlogPostRepository`: Blog post data operations
- `BlogCategoryRepository`: Category management
- `BlogCommentRepository`: Comment operations
- `BlogLikeRepository`: Like/unlike functionality
- `RepositoryManager`: Central repository coordinator

**Usage**:
```python
from petmedia.patterns.repository import repo_manager

# Access data through repositories
posts = repo_manager.posts.get_published()
medication_posts = repo_manager.posts.get_medication_posts()
popular_posts = repo_manager.posts.get_popular_posts(limit=5)
```

## Models

### BlogCategory
- Predefined categories using choices
- Icons for visual representation
- Active/inactive status

### BlogPost
- UUID primary key
- Rich content with excerpts
- SEO fields (slug, meta description)
- Professional advice flags
- Medication-specific fields
- View and like counts
- Featured image support

### BlogComment
- Threaded commenting (basic)
- Approval system
- Author attribution

### BlogLike
- Simple like/unlike functionality
- Prevents duplicate likes per user

## URL Structure

```
/blog/                          # Blog list
/blog/post/<slug>/             # Post detail
/blog/category/<name>/         # Category posts
/blog/professional/            # Professional advice
/blog/medications/             # Medication posts
/blog/create/                  # Create standard post
/blog/create/professional/     # Create professional post
/blog/create/medication/       # Create medication post
/blog/search/                  # Search posts
```

## Templates

- `blog_list.html`: Main blog listing with sidebar
- `blog_detail.html`: Single post view with comments
- `create_post.html`: Post creation form
- Categories and search views (to be created)

## Forms

- `BlogPostForm`: Standard post creation
- `ProfessionalBlogPostForm`: Professional advice posts
- `MedicationBlogPostForm`: Medication-specific posts
- `CommentForm`: Comment submission

## Admin Interface

Comprehensive admin interface with:
- Post management with filtering and search
- Category management
- Comment moderation
- User-friendly field organization

## Installation & Setup

1. **Add to INSTALLED_APPS**:
```python
INSTALLED_APPS = [
    # ... other apps
    'petmedia',
]
```

2. **Include URLs**:
```python
urlpatterns = [
    # ... other patterns
    path('blog/', include('petmedia.urls', namespace='petmedia')),
]
```

3. **Run Migrations**:
```bash
python manage.py makemigrations petmedia
python manage.py migrate
```

4. **Create Categories**:
```bash
python manage.py create_blog_categories
```

## Usage Examples

### Creating Posts

```python
# Standard post by pet owner
post_data = {
    'title': 'My Dog\'s Recovery Story',
    'content': 'Here\'s how we helped our dog recover...',
    'category': medication_category,
}
post = BlogPostFactory.create_post('standard', owner_user, post_data)

# Professional advice by vet
advice_data = {
    'title': 'Understanding Pet Allergies',
    'content': 'As a veterinarian, I often see...',
    'is_professional_advice': True,
}
post = BlogPostFactory.create_post('professional', vet_user, advice_data)

# Medication guide
med_data = {
    'title': 'Rimadyl for Dogs: Complete Guide',
    'content': 'Rimadyl is a common NSAID...',
    'medication_name': 'Rimadyl (Carprofen)',
    'dosage_info': '2mg per pound twice daily',
    'side_effects': 'Possible GI upset, monitor appetite',
}
post = BlogPostFactory.create_post('medication', vet_user, med_data)
```

### Querying Data

```python
# Get posts by category
nutrition_posts = repo_manager.posts.get_by_category(nutrition_category)

# Search posts
search_results = repo_manager.posts.search_posts('flea treatment')

# Get professional posts only
professional_posts = repo_manager.posts.get_professional_posts()

# Get paginated posts with filters
page = repo_manager.posts.get_paginated_posts(
    page=1, 
    per_page=10,
    filters={'category': medication_category, 'is_professional': True}
)
```

## Security Features

- User permission checking for professional posts
- Content validation
- CSRF protection
- User authentication required for interactions

## Future Enhancements

- Rich text editor for post content
- Image galleries for posts
- Post sharing on social media
- Email subscriptions for new posts
- Advanced search with filters
- Post series/collections
- User profiles and following system
- Mobile responsive design improvements

## Dependencies

- Django (core framework)
- Pillow (image handling)
- django-crispy-forms (form styling, optional)
- django-summernote (rich text editor, optional)

## Contributing

1. Follow Django best practices
2. Maintain the design pattern implementations
3. Add tests for new features
4. Update documentation for changes
5. Ensure mobile responsiveness

## Notes

- The app uses UUID primary keys for security
- Professional advice posts require veterinarian role
- Categories are predefined to maintain consistency
- All user-generated content should be properly sanitized
- The observer pattern enables easy extension for notifications
