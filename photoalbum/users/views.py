from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F
from django.db.models.functions import RowNumber
from django.db.models.expressions import Window, Subquery

from .models import User
from imagesapp.models import Country, County, City, Image, Category
from imagesapp.forms import ImageModifyForm

def register(request):

    if request.method == 'POST':
        """ get form values """
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        location = request.POST['location']
        password = request.POST['password']
        password2 = request.POST['password2']
        location = request.POST['location']
        city = City.objects.get(id=location)

        """ check if passwords match """
        if password == password2:
            """ check username """
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('register')
                else:
                    """ register user """
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        location=city
                    )
                    
                    user.save()
                    messages.success(request, 'You are now registered and can log in')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

    countries = Country.objects.order_by('-name')
    counties = County.objects.order_by('-name')
    cities = City.objects.order_by('-name')

    context = {
        'countries': countries,
        'counties': counties,
        'cities': cities
    }

    return render(request, 'users/register.html', context)

def login(request):

    if request.method == 'POST':
        """ login user """
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
           
            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET.get('next'))

            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials')    
            return redirect('login')

    return render(request, 'users/login.html')

def logout(request):

    if request.user.is_authenticated:
        if request.method == 'POST':
            auth.logout(request)
            messages.success(request, 'You are now logged out')
            return redirect('index')
    
    return redirect('index')

@login_required
def my_images(request, user_id):

    if request.user.id == user_id:

        user_images = Image.objects.filter(user_id=user_id).order_by('-upload_date')
        #user_images = Image.objects.all().order_by('-upload_date')
        categories = Category.objects.values('id', 'name').all()
        cities = City.objects.values('id', 'name').order_by('-name')
        form = ImageModifyForm()

        paginator = Paginator(user_images, 6)
        page = request.GET.get('page')
        paged_images = paginator.get_page(page)

        context = {
            'images': paged_images,
            'categories': categories,
            'cities': cities,
            'form': form
        }
        
        return render(request, 'users/my_images.html', context)
    else:
        return HttpResponseForbidden()

def leaderboard(request):
    
    #SELECT "USERS_USER"."USERNAME", COUNT("IMAGESAPP_IMAGE"."USER_ID") AS "IMAGE__USER__COUNT"
    #FROM "USERS_USER"
    #LEFT OUTER JOIN "IMAGESAPP_IMAGE" ON ("USERS_USER"."ID" = "IMAGESAPP_IMAGE"."USER_ID")
    #GROUP BY "USERS_USER"."USERNAME"
    leaderboard_users = User.objects.values('id', 'username') \
                            .annotate(image_count=Count('image__user')) \
                            .order_by('-image_count')
    
    if 'username' in request.GET:
        username = request.GET.get('username')
        if username:
            leaderboard_users = leaderboard_users.filter(username__icontains=username)
        
    paginator = Paginator(leaderboard_users, 9)
    page = request.GET.get('page')
    paged_leaderboard = paginator.get_page(page)

    context = {
        'users': paged_leaderboard
    }

    return render(request, 'users/leaderboard.html', context)

def profile(request, user_id):
    # TODO user rank

    #SELECT "USERS_USER"."USERNAME", "USERS_USER"."FIRST_NAME", "USERS_USER"."LAST_NAME", "USERS_USER"."EMAIL",
    #       "IMAGESAPP_CITY"."NAME", "USERS_USER"."DATE_JOINED", "IMAGESAPP_COUNTRY"."NAME"
    #FROM "USERS_USER"
    #LEFT OUTER JOIN "IMAGESAPP_CITY" ON ("USERS_USER"."LOCATION_ID" = "IMAGESAPP_CITY"."ID")
    #LEFT OUTER JOIN "IMAGESAPP_COUNTRY" ON ("IMAGESAPP_CITY"."COUNTRY_ID" = "IMAGESAPP_COUNTRY"."ID")
    queryset_user_data = User.objects.values(
        'username',
        'first_name',
        'last_name',
        'email',
        'location__name',
        'date_joined',
        'location__country__name'
    ).annotate(image_count=Count('image__user'))
    # a fenti query-hez még egy where feltétel társul a pk=user_id szerint
    user = get_object_or_404(queryset_user_data, pk=user_id)

    #SELECT "IMAGESAPP_IMAGE"."ID", "IMAGESAPP_IMAGE"."NAME", "IMAGESAPP_IMAGE"."DESCRIPTION", "IMAGESAPP_IMAGE"."PHOTO"
    #FROM "IMAGESAPP_IMAGE"
    #WHERE "IMAGESAPP_IMAGE"."USER_ID" = user_id -> (the actual user_id come from url)
    #ORDER BY "IMAGESAPP_IMAGE"."UPLOAD_DATE" DESC
    user_images = Image.objects.only(
        'photo',
        'name',
        'description',
        'user'
    ).filter(user_id=user_id).order_by('-upload_date')

    user_rank = User.objects.raw(
        'SELECT a.ROW_NUMBER, a.id \
        FROM ( \
            SELECT "USERS_USER"."ID", "USERS_USER"."USERNAME", ROW_NUMBER() OVER (ORDER BY COUNT("IMAGESAPP_IMAGE"."USER_ID") desc ) AS "ROW_NUMBER" \
            FROM "USERS_USER" \
            LEFT OUTER JOIN "IMAGESAPP_IMAGE" ON ("USERS_USER"."ID" = "IMAGESAPP_IMAGE"."USER_ID") \
            GROUP BY "USERS_USER"."USERNAME", "USERS_USER"."ID" \
        ) a \
        where a.id = ' + str(user_id)
    )[:1]

    paginator = Paginator(user_images, 6)
    page = request.GET.get('page')
    paged_user_images = paginator.get_page(page)

    context = {
        'user': user,
        'user_images': paged_user_images,
        'user_rank': user_rank
    }

    return render(request, 'users/profile.html', context)