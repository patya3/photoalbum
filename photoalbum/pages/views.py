from datetime import datetime
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.db.models import Count, Max

from imagesapp.models import Image, City

def index(request):
    images = Image.objects.order_by('-upload_date')[:6]

    # upload statistics
    now = datetime.now()

    # SELECT COUNT("IMAGESAPP_IMAGE"."ID") AS "IMAGE_COUNT"
    # FROM "IMAGESAPP_IMAGE"
    # WHERE EXTRACT(DAY FROM CAST((FROM_TZ("IMAGESAPP_IMAGE"."UPLOAD_DATE", '0:00') AT TIME ZONE 'UTC') AS TIMESTAMP)) = 12
    daily_upload = Image.objects.filter(upload_date__day=now.day).aggregate(image_count=Count('id'))
    monthly_upload = Image.objects.filter(upload_date__month=now.month).aggregate(image_count=Count('id'))
    yearly_upload = Image.objects.filter(upload_date__year=now.year).aggregate(image_count=Count('id'))
    all_time_upload = Image.objects.aggregate(image_count=Count('id'))

    # SELECT "IMAGESAPP_IMAGE"."CITY_ID", "IMAGESAPP_CITY"."NAME", COUNT("IMAGESAPP_IMAGE"."ID") AS "IMAGE_COUNT"
    # FROM "IMAGESAPP_IMAGE"
    # INNER JOIN "IMAGESAPP_CITY" ON ("IMAGESAPP_IMAGE"."CITY_ID" = "IMAGESAPP_CITY"."ID")
    # GROUP BY "IMAGESAPP_IMAGE"."CITY_ID", "IMAGESAPP_CITY"."NAME"
    # ORDER BY "IMAGE_COUNT" DESC
    # FETCH FIRST 1 ROWS ONLY
    first_city = Image.objects.values('city_id', 'city__name').annotate(image_count=Count('id')).order_by('-image_count')[:1]

    context = {
        'images': images,
        'statistics': {
            'daily': daily_upload['image_count'],
            'monthly': monthly_upload['image_count'],
            'yearly': yearly_upload['image_count'],
            'all_time': all_time_upload['image_count'],
            'first_city': first_city
        }
    }
    return render(request, 'pages/index.html', context)