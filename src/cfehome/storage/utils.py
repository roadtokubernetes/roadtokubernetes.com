from django.conf import settings
from django.core.files.storage import get_storage_class

from . import backends


def get_public_storage():
    _Storage = backends.MediaPublicS3BotoStorage
    if settings.DEBUG:
        _Storage = get_storage_class()
    return _Storage()
