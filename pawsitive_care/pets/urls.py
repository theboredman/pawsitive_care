from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    # Pet management
    path('', views.pet_list, name='pet_list'),
    path('create/', views.pet_create, name='pet_create'),
    path('<int:pk>/', views.pet_detail, name='pet_detail'),
    path('<int:pk>/update/', views.pet_update, name='pet_update'),
    path('<int:pk>/delete/', views.pet_delete, name='pet_delete'),
    
    # Medical records
    path('<int:pk>/medical/add/', views.add_medical_record, name='add_medical_record'),
    path('medical/<int:record_id>/edit/', views.edit_medical_record, name='edit_medical_record'),
    path('medical/<int:record_id>/delete/', views.delete_medical_record, name='delete_medical_record'),
    
    # Documents
    path('<int:pk>/document/upload/', views.upload_document, name='upload_document'),
    path('document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    
    # Search
    path('search/', views.search_pets, name='search_pets'),
    
    # Photos
    path('<int:pk>/photo/add/', views.pet_photo_add, name='pet_photo_add'),
    path('photo/<int:photo_id>/delete/', views.pet_photo_delete, name='pet_photo_delete'),
]
