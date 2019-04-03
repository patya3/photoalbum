from django import forms
from .models import Image

from django.contrib.auth.models import auth

class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['name', 'description', 'photo', 'category', 'city']
        exclude = ['user']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs = {
                'class': 'form-control'
            }
