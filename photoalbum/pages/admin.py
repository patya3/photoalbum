from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models as dj_models
from ckeditor.widgets import CKEditorWidget
from django_summernote.admin import SummernoteWidget

# Register your models here.
class MyFlatPageAdmin(FlatPageAdmin):
    filter_horizontal = ['sites']
    prepopulated_fields = {'url': ('title',)}
    formfield_overrides = {
        dj_models.TextField: {'widget': SummernoteWidget(attrs={'width': '100%', 'height': '500'})}
    }
    

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, MyFlatPageAdmin)