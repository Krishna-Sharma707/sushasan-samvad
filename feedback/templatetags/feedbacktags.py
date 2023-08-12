from django import template
from ..views import is_district_admin, is_village_admin

register = template.Library()


@register.simple_tag
def dist_admin(user):
    return is_district_admin(user)


@register.simple_tag
def village_admin(user):
    return is_village_admin(user)
