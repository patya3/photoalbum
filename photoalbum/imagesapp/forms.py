from django import forms
from .models import Images


class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = Images
        fields = ['name', 'description', 'photo']
        
    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['description'].widget.attrs = {
            'class': 'form-control'
        }
        self.fields['photo'].widget.attrs = {
            'class': 'form-control'
        }