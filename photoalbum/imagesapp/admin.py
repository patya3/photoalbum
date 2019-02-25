from django.contrib import admin

from .models import Images


class ImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_per_page = 25


admin.site.register(Images, ImagesAdmin)