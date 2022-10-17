import pathlib

from cfehome.storage import backends
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.text import slugify


def get_profile_image_upload_to(instance, filename):
    fpath = pathlib.Path(filename)
    slug = slugify(instance.username)
    return f"u/{slug}{fpath.suffix}"


def get_profile_storage():
    _Storage = backends.MediaPublicS3BotoStorage
    if settings.DEBUG:
        _Storage = get_storage_class()
    return _Storage()
