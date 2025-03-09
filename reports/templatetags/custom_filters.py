from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """ Safe dictionary lookup for Django templates """
    return dictionary.get(key, {'code': '-', 'comment': '-'})
