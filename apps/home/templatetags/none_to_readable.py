from django import template

register = template.Library()


@register.filter
def none_to_readable(value):
    if value == None or value == "None":
        return "Невідомо"
    return value