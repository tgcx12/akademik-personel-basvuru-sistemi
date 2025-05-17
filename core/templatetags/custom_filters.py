from django import template

register = template.Library()

@register.filter
def get_ad(value):
    try:
        return value.split(' ')[0]
    except:
        return ''

@register.filter
def get_soyad(value):
    try:
        return ' '.join(value.split(' ')[1:])
    except:
        return ''
