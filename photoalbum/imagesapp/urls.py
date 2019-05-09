from django.urls import path
from . import views

urlpatterns = [
    path('upload_image', views.upload_image, name='upload_image'),
    path('', views.index, name='list_images'),
    path('<int:image_id>', views.image, name='image'),
    path('update_image/<int:image_id>', views.update_image, name='update_image'),
    path('delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('json_load', views.json_load),
    path('rate_image/<int:image_id>', views.rate_image, name='rate_image')
]