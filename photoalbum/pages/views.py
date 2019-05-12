from django.shortcuts import render
from imagesapp.models import Image

def index(request):
    images = Image.objects.order_by('-upload_date')[:6]

    context = {
        'images': images
    }
    return render(request, 'pages/index.html', context)