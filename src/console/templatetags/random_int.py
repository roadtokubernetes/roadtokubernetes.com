import random

from django import template

register = template.Library()


@register.simple_tag
def random_int(a=4_000, b=100_000):
    return random.randint(a, b)
