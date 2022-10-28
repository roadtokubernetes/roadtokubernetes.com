from cfehome.storage.backends import MediaPublicS3BotoStorage
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def get_public_storage():
    return FileSystemStorage() if settings.DEBUG else MediaPublicS3BotoStorage()
