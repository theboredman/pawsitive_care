from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # Add records URLs here
    path('', views.records_list, name='records_list'),
]
