from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    location = models.ForeignKey('imagesapp.City', on_delete=models.SET_NULL, blank=True, null=True)