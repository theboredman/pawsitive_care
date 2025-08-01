from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Add appointment URLs here
    path('', views.appointment_list, name='appointment_list'),
]
