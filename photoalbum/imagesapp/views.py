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
from django.db.models import Count, Avg, Max

from .models import Image, Category, Country, County, City, Rating
from .forms import ImageUploadForm, ImageModifyForm, ImageRateForm
import import_script

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


    # SELECT "IMAGESAPP_CATEGORY"."ID", "IMAGESAPP_CATEGORY"."NAME", "IMAGESAPP_CATEGORY"."PARENT_CATEGORY_ID", COUNT("IMAGESAPP_IMAGE"."ID") AS "IMAGE_COUNT"
    # FROM "IMAGESAPP_CATEGORY"
    # LEFT OUTER JOIN "IMAGESAPP_IMAGE" ON ("IMAGESAPP_CATEGORY"."ID" = "IMAGESAPP_IMAGE"."CATEGORY_ID")
    # GROUP BY "IMAGESAPP_CATEGORY"."ID", "IMAGESAPP_CATEGORY"."NAME", "IMAGESAPP_CATEGORY"."PARENT_CATEGORY_ID"
    # ORDER BY "IMAGESAPP_CATEGORY"."PARENT_CATEGORY_ID" DESC
    categories = Category.objects.annotate(image_count=Count('image__id')).order_by('-parent_category_id')

    # SELECT "IMAGESAPP_CITY"."ID", "IMAGESAPP_CITY"."NAME", "IMAGESAPP_CITY"."COUNTRY_ID", "IMAGESAPP_CITY"."COUNTY_ID", COUNT("IMAGESAPP_IMAGE"."ID") AS "IMAGE_COUNT"
    # FROM "IMAGESAPP_CITY"
    # LEFT OUTER JOIN "IMAGESAPP_IMAGE" ON ("IMAGESAPP_CITY"."ID" = "IMAGESAPP_IMAGE"."CITY_ID")
    # GROUP BY "IMAGESAPP_CITY"."ID", "IMAGESAPP_CITY"."NAME", "IMAGESAPP_CITY"."COUNTRY_ID", "IMAGESAPP_CITY"."COUNTY_ID"
    # ORDER BY "IMAGESAPP_CITY"."NAME" DESC
    cities = City.objects.values(
        'id',
        'name',
        'country_id',
        'county_id'
        ).annotate(image_count=Count('image__id')).order_by('-name')

    counties = County.objects.order_by('-name')

    countries = Country.objects.values('id', 'name').order_by('-name')

    # SELECT "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."PHOTO", AVG("IMAGESAPP_RATING"."STARS") AS "RATE_AVG"
    # FROM "IMAGESAPP_IMAGE"
    # LEFT OUTER JOIN "IMAGESAPP_RATING" ON ("IMAGESAPP_IMAGE"."ID" = "IMAGESAPP_RATING"."IMAGE_ID")
    # GROUP BY "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."PHOTO", "IMAGESAPP_IMAGE"."UPLOAD_DATE"
    # ORDER BY "IMAGESAPP_IMAGE"."UPLOAD_DATE" DESC
    images = Image.objects.defer('rating__comment').only(
        'id',
        'name',
        'photo'
        ).annotate(rate_avg=Avg('rating__stars')).order_by('-upload_date')

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

    top_in_category = None
    if 'category' in request.GET:
        category = request.GET['category']
        if category and int(category) != -1:
            images = images.filter(Q(category_id=category) |
                                   Q(category__parent_category_id=category))


            # SELECT "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."PHOTO", AVG("IMAGESAPP_RATING"."STARS") AS "AVG_RATING", COUNT("IMAGESAPP_RATING"."ID") AS "COUNT_RATING"
            # FROM "IMAGESAPP_IMAGE"
            # LEFT OUTER JOIN "IMAGESAPP_RATING" ON ("IMAGESAPP_IMAGE"."ID" = "IMAGESAPP_RATING"."IMAGE_ID")
            # WHERE "IMAGESAPP_IMAGE"."CATEGORY_ID" = 9
            # GROUP BY "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."PHOTO"
            # HAVING NOT (AVG("IMAGESAPP_RATING"."STARS") IS NULL)
            # ORDER BY "AVG_RATING" DESC  FETCH FIRST 1 ROWS ONLY
            top_in_category = Image.objects.filter(
                    Q(category_id=category) | Q(category__parent_category_id=category)
                ).only(
                'id',
                'name',
                'photo'
                ).annotate(
                    avg_rating=Avg('rating__stars')
                    ).annotate(
                        count_rating=Count('rating__id')
                        ).filter(~Q(avg_rating=None)).order_by('-avg_rating')[:1]

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

    if top_in_category is not None and top_in_category:
        context.update({'top_in_category': top_in_category[0]})

    if request.is_ajax():
        template = page_template

    return render(request, template, context)

def image(request, image_id, new_context = {}):
    """ image subpage with rating """
    image = get_object_or_404(Image, pk=image_id)
    ratings = Rating.objects.filter(image_id=image_id).order_by('-id')

    form = ImageRateForm()

    context = {
        'image': image,
        'form': form,
        'ratings': ratings
    }
    context.update(new_context)

    return render(request, 'imagesapp/image.html', context)

@require_POST
def update_image(request, image_id):
    """ update a image's data """
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

@login_required
@require_POST
def rate_image(request, image_id):
    """ rate image with comment on image subpage """
    if request.user.is_authenticated:
        form = ImageRateForm(data=request.POST)

        if form.is_valid():
            rateModel = form.save(commit=False)
            rateModel.image = get_object_or_404(Image, pk=image_id)
            rateModel.save()

            messages.success(request, 'Successfully rated the Image.')
            return HttpResponseRedirect(reverse('image', args=[image_id]))
        else:
            return image(request, image_id, {'form': form, 'errors': form.errors})
    
    return HttpResponse(status=200)

def cities_faces(request):
    """ cities faces | of the 4 best rated photos from that city """

    # SELECT "IMAGESAPP_IMAGE"."PHOTO", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_CITY"."NAME", AVG("IMAGESAPP_RATING"."STARS") AS "RATE_AVG"
    # FROM "IMAGESAPP_IMAGE"
    # INNER JOIN "IMAGESAPP_CITY" ON ("IMAGESAPP_IMAGE"."CITY_ID" = "IMAGESAPP_CITY"."ID")
    # LEFT OUTER JOIN "IMAGESAPP_RATING" ON ("IMAGESAPP_IMAGE"."ID" = "IMAGESAPP_RATING"."IMAGE_ID")
    # GROUP BY "IMAGESAPP_IMAGE"."PHOTO", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_CITY"."NAME"
    # ORDER BY "RATE_AVG" ASC
    cities_images = Image.objects.defer('rating__comment').only(
        'photo',
        'name',
        'id',
        'city__id'
        ).annotate(rate_avg=Avg('rating__stars')).order_by('rate_avg')
    cities = City.objects.only('name', 'id')

    cities_faces = []
    for city in cities:
        cities_faces.append({
            'city_id': city.id,
            'city_name': city.name,
            'citys_images': []
        })

    for e in cities_faces:
        for i in cities_images:
            if i.city_id == e['city_id'] and len(e['citys_images']) < 4:
                e['citys_images'].append(i)

    cities_faces = [city for city in cities_faces if len(city['citys_images']) > 0]

    if 'city' in request.GET:
        city_id = int(request.GET['city'])
        if city_id and city_id != -1:
            cities_faces = list(filter(lambda c: c['city_id'] == city_id, cities_faces))

    context = {
        'cities_images': cities_faces,
        'cities': cities,
        'values': request.GET
    }

    return render(request, 'imagesapp/cities_faces.html', context)

def popular_destiantions(request):
    """ list the 5 most popular destinations with 
    images that were not uploaded by users who live there  """
    
    # SELECT (to_char(imagesapp_city.description)) AS "CHAR_DESC", "IMAGESAPP_IMAGE"."CITY_ID", "IMAGESAPP_CITY"."NAME", COUNT("IMAGESAPP_IMAGE"."ID") AS "COUNT_IMAGE"
    # FROM "IMAGESAPP_IMAGE"
    # INNER JOIN "IMAGESAPP_CITY" ON ("IMAGESAPP_IMAGE"."CITY_ID" = "IMAGESAPP_CITY"."ID")
    # INNER JOIN "USERS_USER" ON ("IMAGESAPP_IMAGE"."USER_ID" = "USERS_USER"."ID")
    # WHERE NOT ("IMAGESAPP_IMAGE"."CITY_ID" = ("USERS_USER"."LOCATION_ID"))
    # GROUP BY "IMAGESAPP_IMAGE"."CITY_ID", "IMAGESAPP_CITY"."NAME", (to_char(imagesapp_city.description))
    # ORDER BY "COUNT_IMAGE" DESC
    # FETCH FIRST 5 ROWS ONLY
    popular_cities = Image.objects.extra(
        select={'char_desc': 'to_char(imagesapp_city.description)'}
        ).values(
            'city_id',
            'city__name',
            'char_desc'
            ).filter(
                ~Q(city_id=F('user__location_id'))
                ).annotate(count_image=Count('id')).order_by('-count_image')[:5]

    # SELECT "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."PHOTO", "IMAGESAPP_IMAGE"."CITY_ID", MAX("IMAGESAPP_RATING"."STARS") AS "MAX_RATE"
    # FROM "IMAGESAPP_IMAGE"
    # LEFT OUTER JOIN "IMAGESAPP_RATING" ON ("IMAGESAPP_IMAGE"."ID" = "IMAGESAPP_RATING"."IMAGE_ID")
    # GROUP BY "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."PHOTO", "IMAGESAPP_IMAGE"."CITY_ID", "IMAGESAPP_IMAGE"."UPLOAD_DATE"
    # ORDER BY "MAX_RATE" ASC, "IMAGESAPP_IMAGE"."UPLOAD_DATE" DESC
    main_images = Image.objects.only(
        'id',
        'city_id',
        'photo'
        ).annotate(max_rate=Max('rating__stars')).order_by('max_rate', '-upload_date')

    for city in popular_cities:
        city['main_image'] = None
        for i in main_images:
            if i.city_id == city['city_id'] and city['main_image'] is None:
                city['main_image'] = i.photo

    context = {
        'popular_cities': popular_cities
    }

    return render(request, 'imagesapp/popular_destinations.html', context)

def json_load(request):
    """ for import data to database from json files """
    import_script.load_pop()
    return HttpResponse(status=200)
