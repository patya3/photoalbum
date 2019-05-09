import json

from imagesapp.models import Country, City


def load_pop():

    countries = Country.objects.values('name', 'id')
    city_db = [city['name'] for city in City.objects.values('name')]

    with open('population.json') as cities:
        data = json.load(cities)
        for item in countries:
            pop_data = [{
                'city': c['City'].title(),
                'value': c['Value'],
                'country': c['Country or Area'],
                'year': c['Source Year']
            } for c in data if c['Country or Area'] == item['name'] and c['City type'] == 'City proper']
            bubble_sort(pop_data)

            real_data = []

            for c in pop_data:
                if c['city'] not in [k['city'] for k in real_data] \
                    and c['city'] not in city_db:
                    real_data.append(c)
            for city in real_data[:10]:
                desc = 'Beatiful city in ' + city['country'] + '.'
                country_id = [c['id'] for c in countries if c['name'] == city['country']]
                print(city['country'])
                c = City(
                    name=city['city'],
                    description=desc,
                    country=Country.objects.get(pk=country_id[0]),
                    county=None)
                c.save()

def bubble_sort(data):
    """ sorting by population """
    for i in range(len(data)):
        for j in range(0, len(data)-i-1):
            if float(data[j]['value']) < float(data[j+1]['value']):
                data[j], data[j+1] = data[j+1], data[j]
