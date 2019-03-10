from django.contrib import admin

from .models import Image, Category, City, Country, Rating, County


class ImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_per_page = 25


admin.site.register(Image, ImagesAdmin)
admin.site.register(Category)
admin.site.register(City)
admin.site.register(Country)
admin.site.register(County)
admin.site.register(Rating)
