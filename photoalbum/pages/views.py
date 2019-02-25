from django.shortcuts import render
from imagesapp.models import Images

def index(request):
    images = Images.objects.order_by('-upload_date')[:3]

    context = {
        'images': images
    }
    return render(request, 'pages/index.html', context)