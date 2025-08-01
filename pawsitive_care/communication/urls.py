from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Add communication URLs here
    path('', views.communication_list, name='communication_list'),
]
