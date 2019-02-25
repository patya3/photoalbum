from django.db import models
from django.core.validators import MaxLengthValidator
from datetime import datetime


class Images(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    upload_date = models.DateTimeField(default=datetime.now, blank=True)

    def remove_on_image_update(self):
        try:
            obj = Images.objects.get(id=self.id)
        except Images.DoesNotExist:
            return
        if obj.photo and self.photo and obj.photo != self.photo:
            obj.photo.delete()

    def delete(self, *args, **kwargs):
        self.photo.delete()
        return super(Images, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.remove_on_image_update()
        return super(Images, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name