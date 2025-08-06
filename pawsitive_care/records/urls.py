from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # Add records URLs here
    path('add/', views.add_record, name='add_record'),
    path('', views.view_records, name='view_records'),
    path('my-pets/', views.my_pet_records, name='my_pet_records'),
    path('records/<int:record_id>/', views.record_detail, name='record_detail'),
]
