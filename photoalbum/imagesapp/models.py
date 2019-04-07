from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils import timezone

from users.models import User
from photoalbum.settings import MEDIA_ROOT

import uuid
import os

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('photos', filename)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent_category = models.ForeignKey('self', default=0, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
    county = models.ForeignKey(County, on_delete=models.DO_NOTHING, default=0, blank=True, null=True)

    def __str__(self):
        return self.name


class Image(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)
    photo = models.ImageField(upload_to=get_file_path)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING)
    upload_date = models.DateTimeField(default=timezone.now, blank=True)

    def remove_on_image_update(self):
        try:
            obj = Image.objects.get(id=self.id)
        except Image.DoesNotExist:
            return
        if obj.photo and self.photo and obj.photo != self.photo:
            obj.photo.delete()

    def delete(self, *args, **kwargs):
        self.photo.delete()
        return super(Image, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.remove_on_image_update()
        return super(Image, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Rating(models.Model):
    stars = models.IntegerField(blank=False, null=False)
    comment = models.TextField(max_length=500, null=True, blank=True)
    image = models.ForeignKey(Image, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.comment