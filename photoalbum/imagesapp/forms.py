from django import forms
from .models import Image, Rating

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


class ImageModifyForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['name', 'description', 'category', 'city']
        
    def __init__(self, *args, **kwargs):
        super(ImageModifyForm, self).__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs = {
                'class': 'form-control'
            }


class ImageRateForm(forms.ModelForm):
    
    class Meta:
        model = Rating
        fields = ['stars', 'comment']

    def __init__(self, *args, **kwargs):
        super(ImageRateForm, self).__init__(*args, **kwargs)

        self.fields['stars'].widget.attrs = {
            'class': 'form-control width-10',
            'min':'0',
            'max': '5'
        }

        self.fields['comment'].widget.attrs = {
            'class': 'form-control'
        }