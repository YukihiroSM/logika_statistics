from django import template

register = template.Library()


@register.filter
def count_conversion(value):
    conversion = None
    if value.get("payments") == 0 and value.get("attended") == 0:
        conversion = 0
    else:
        try:
            conversion = round(
                (value.get("payments") / value.get("attended")) * 100, 2)
        except ZeroDivisionError:
            conversion = 100
    return conversion