from django import template

register = template.Library()


@register.filter(name='get_item_lesson')
def get_item_lesson(dictionary, key):
    return int(dictionary.get(key)) - 2
