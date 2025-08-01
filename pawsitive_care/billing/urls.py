from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Add billing URLs here
    path('', views.billing_list, name='billing_list'),
]
