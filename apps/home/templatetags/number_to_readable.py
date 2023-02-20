from django import template

register = template.Library()


@register.filter
def number_to_readable(value):
    return "Так" if value == 1 else "Ні"