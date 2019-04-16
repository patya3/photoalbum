from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import auth
from django.db.models import Q, F
from django.http import HttpResponse, HttpResponseForbidden
from datetime import date
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import Image, Category, Country, County, City
from .forms import ImageUploadForm, ImageModifyForm

@login_required
def upload_image(request):

    if request.method == 'POST':

        """ upload photo """
        form = ImageUploadForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            imageModel = form.save(commit=False)
            imageModel.user = request.user
            imageModel.save()

            messages.success(request, 'Successfully uploaded')
            return redirect('upload_image')
        else:
            return render(request, 'imagesapp/upload_image.html', {'form': form, 'errors': form.errors})    
    else:
        categories = Category.objects.order_by('-name')
        form = ImageUploadForm(user=request.user)

        context = {
            'categories': categories,
            'form': form
        }
        return render(request, 'imagesapp/upload_image.html', context)

    return HttpResponseRedirect('upload_image')

@require_http_methods(["GET", "POST"])
def index(request,
            template='imagesapp/list_images.html',
            page_template='partials/_image_list.html'):

    categories = Category.objects.annotate(image_count=Count('image__id')).order_by('-parent_category_id')
    cities = City.objects.values('id', 'name', 'country_id', 'county_id').order_by('-name')
    counties = County.objects.order_by('-name')
    countries = Country.objects.values('id', 'name').order_by('-name')

    images = Image.objects.order_by('-upload_date')
    new_categories = []
    for category in categories:
        new_categories.append({
            'id': category.id,
            'name': category.name,
            'image_count': category.image_count,
            'parent_category_id': category.parent_category_id,
            'subcategories': []
        })

    for category in new_categories:
        if category['parent_category_id'] not in {0, None}:
            for parent_cat in new_categories:
                if category['parent_category_id'] == parent_cat['id']:
                    parent_cat['subcategories'].append(category)
                    parent_cat['image_count'] = parent_cat['image_count'] + category['image_count']

    categories = [cat for cat in new_categories if cat['parent_category_id'] is None]

    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            images = images.filter(Q(name__icontains=keywords) |
                                   Q(description__icontains=keywords))
    
    if 'country' in request.GET:
        country = request.GET['country']
        if country and int(country) != -1:
            images = images.filter(city__country__id=country)
    
    if 'county' in request.GET:
        county = request.GET['county']
        if county and int(county) != -1:
            images = images.filter(city__county__id=county)

    if 'city' in request.GET:
        city = request.GET['city']
        if city and int(city) != -1:
            images = images.filter(city_id=city)

    if 'category' in request.GET:
        category = request.GET['category']
        if category and int(category) != -1:
            images = images.filter(Q(category_id=category) |
                                   Q(category__parent_category_id=category))

    if 'date_from' in request.GET:
        date_from = request.GET['date_from'].split('-')
        if date_from[0] != '':
            images = images.filter(upload_date__gt=date(int(date_from[0]),
                                                        int(date_from[1]),
                                                        int(date_from[2])))

    if 'date_to' in request.GET:
        date_to = request.GET['date_to'].split('-')
        if date_to[0] != '':
            images = images.filter(upload_date__lt=date(int(date_to[0]),
                                                        int(date_to[1]),
                                                        int(date_to[2])))

    context = {
        'images': images,
        'filters': {
            'countries': countries,
            'counties': counties,
            'cities': cities
        },
        'categories': categories,
        'values': request.GET
    }

    if request.is_ajax():
        template = page_template

    return render(request, template, context)

def image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)

    context = {
        'image': image
    }

    return render(request, 'imagesapp/image.html', context)

""" JOBB LENNE AJAX-AL """
@require_POST
def update_image(request, image_id):

    if request.method == 'POST':
        image = Image.objects.get(pk=image_id)
        if request.user == image.user:
            image_update_form = ImageModifyForm(data=request.POST, instance=image)

            if image_update_form.is_valid():
                form = image_update_form.save(commit=False)
                form.save()

                return HttpResponseRedirect(reverse('my_images', args=[request.user.id]))
            else:
                form = ImageModifyForm(instance=image)
        
        return HttpResponseForbidden()

@require_GET
def delete_image(request, image_id):
    
    if request.method == 'GET':
        print(request.GET)
        image = Image.objects.get(pk=image_id)
        if request.user == image.user:
            image.delete()

            return HttpResponse(status=200)