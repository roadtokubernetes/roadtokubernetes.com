from cfehome import utils
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext as _

project_id_restricted_list = ["google", "ssl"]


def valid_project_id(value):
    blocklist = utils.blocklist.data
    blocklist_slugified = [slugify(x) for x in blocklist]
    if value in blocklist:
        raise ValidationError(_(f"{value} is not allowed as a project id."))
    if value in blocklist_slugified:
        raise ValidationError(_(f"{value} is not a valid project id."))
