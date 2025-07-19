from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=False)
    address = models.TextField(blank=False)

    def __str__(self):
        return self.username
