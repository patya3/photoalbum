from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import auth
from django.db.models import Q

from .models import Image, Category, Country, County, City
from .forms import ImageUploadForm


def upload_image(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            print(request)
            """ upload photo """
            form = ImageUploadForm(data=request.POST,files=request.FILES)

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
    else:
        return redirect('login')

def index(request):
    categories = Category.objects.order_by('-id')
    cities = City.objects.values('id', 'name', 'country_id', 'county_id').order_by('-name')
    counties = County.objects.order_by('-name')
    countries = Country.objects.values('id', 'name').order_by('-name')

    images = Image.objects.order_by('-upload_date')

    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            images = images.filter(Q(name__icontains=keywords) | Q(description__icontains=keywords))
    
    if 'country' in request.GET:
        country = request.GET['country']
        if country:
            images = images.filter(city__country__id=country)
    
    if 'county' in request.GET:
        county = request.GET['county']
        if county:
            images = images.filter(city__county__id=county)

    if 'city' in request.GET:
        city = request.GET['city']
        if city:
            images = images.filter(city_id=city)

    if 'category' in request.GET:
        category = request.GET['category']
        if category:
            images = images.filter(category_id=category)

    paginator = Paginator(images, 6)
    page = request.GET.get('page')
    paged_images = paginator.get_page(page)


    context = {
        'images': paged_images,
        'filters': {
            'categories': categories,
            'countries': countries,
            'counties': counties,
            'cities': cities
        },
        'values': request.GET
    }
    return render(request, 'imagesapp/list_images.html', context)

def image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)

    context = {
        'image': image
    }

    return render(request, 'imagesapp/image.html', context)