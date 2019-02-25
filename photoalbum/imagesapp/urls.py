from django.urls import path
from . import views

urlpatterns = [
    path('upload_image', views.upload_image, name='upload_image'),
    path('', views.index, name='list_images'),
    path('<int:image_id>', views.image, name='image')
]