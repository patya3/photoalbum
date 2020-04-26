from django import template

register = template.Library()

@register.inclusion_tag('imagesapp/slider.html')
def slider():
    context = {
        'kecske': 'kecske',
        'mecske': 11
    }
    return context