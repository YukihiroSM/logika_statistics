from django import template

register = template.Library()


@register.filter
def replace_space_to_(value):
    return value.replace(" ", "_").replace("'", "")

