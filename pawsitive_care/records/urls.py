from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # Add records URLs here
    path('add/', views.add_record, name='add_record'),
    path('', views.view_records, name='view_records'),
    path('my-pets/', views.my_pet_records, name='my_pet_records'),
    path('record/<int:record_id>/', views.record_detail, name='record_detail'),
    path('records/<int:record_id>/update/', views.update_record, name='update_record'),
    path('records/<int:record_id>/delete/', views.delete_record, name='delete_record'),
    path('surgery/add/', views.add_surgery, name='add_surgery'),
    path('surgery/view/', views.view_surgeries, name='view_surgeries'),
    path('surgery/<int:record_id>/', views.surgery_detail, name='surgery_detail'),
    path('MedicalRecord/add/', views.add_medical_record, name='add_medical_record'),
]
