from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Add inventory URLs here
    path('', views.inventory_list, name='inventory_list'),
]
