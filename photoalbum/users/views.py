from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.urls import reverse
from .models import User
from imagesapp.models import Country, County, City, Image, Category
from imagesapp.forms import ImageModifyForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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