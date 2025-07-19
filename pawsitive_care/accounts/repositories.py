from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class UserRepository:
    @staticmethod
    def get(pk):
        return get_object_or_404(User, pk=pk)
    
    @staticmethod
    def filter(**kwargs):
        return User.objects.filter(**kwargs)
    
    @staticmethod
    def create(**data):
        return User.objects.create(**data)
    
    @staticmethod
    def save(user):
        user.save()
        return user
    