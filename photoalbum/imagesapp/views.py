from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import auth

from .models import Image
from .forms import ImageUploadForm


def upload_image(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            """ upload photo """
            form = ImageUploadForm(data=request.POST,files=request.FILES)

            if form.is_valid():
                imageModel = form.save(commit=False)
                imageModel.save()

                messages.success(request, 'Successfully uploaded')
                return redirect('upload_image')
            else:
                return render(request, 'imagesapp/upload_image.html', {'form': form, 'errors': form.errors})    
        else:
            form = ImageUploadForm()
            return render(request, 'imagesapp/upload_image.html', {'form': form})

        return HttpResponseRedirect('upload_image')
    else:
        return redirect('index')

def index(request):
    images = Image.objects.order_by('-upload_date')

    paginator = Paginator(images, 6)
    page = request.GET.get('page')
    paged_images = paginator.get_page(page)

    context = {
        'images': paged_images
    }
    return render(request, 'imagesapp/list_images.html', context)

def image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)

    context = {
        'image': image
    }

    return render(request, 'imagesapp/image.html', context)