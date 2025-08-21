from django.urls import path
from . import views

app_name = 'petmedia'

urlpatterns = [
    # Blog post URLs
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('post/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('post/<uuid:pk>/like/', views.toggle_like, name='toggle_like'),
    path('post/<uuid:pk>/comment/', views.add_comment, name='add_comment'),
    
    # Category URLs
    path('category/<str:name>/', views.CategoryView.as_view(), name='category'),
    
    # Professional advice URLs
    path('professional/', views.ProfessionalAdviceView.as_view(), name='professional_advice'),
    path('medications/', views.MedicationPostsView.as_view(), name='medications'),
    
    # Create post URLs
    path('create/', views.CreatePostView.as_view(), name='create_post'),
    path('create/professional/', views.CreateProfessionalPostView.as_view(), name='create_professional_post'),
    path('create/medication/', views.CreateMedicationPostView.as_view(), name='create_medication_post'),
    
    # User posts
    path('my-posts/', views.UserPostsView.as_view(), name='user_posts'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Admin post management URLs
    path('admin/posts/', views.admin_post_management, name='admin_post_management'),
    path('admin/posts/<uuid:post_id>/', views.admin_post_detail, name='admin_post_detail'),
    path('admin/posts/<uuid:post_id>/toggle-status/', views.admin_toggle_post_status, name='admin_toggle_post_status'),
    path('admin/posts/<uuid:post_id>/toggle-featured/', views.admin_toggle_post_featured, name='admin_toggle_post_featured'),
    path('admin/posts/<uuid:post_id>/delete/', views.admin_delete_post, name='admin_delete_post'),
    
    # AJAX endpoints
    path('ajax/categories/', views.get_categories_ajax, name='ajax_categories'),
]
