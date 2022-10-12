from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage

from . import mixins


class PublicS3Boto3Storage(mixins.DefaultACLMixin, S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class MediaS3BotoStorage(mixins.DefaultACLMixin, S3Boto3Storage):
    location = 'media'
    default_acl = 'private'


class CachedS3Boto3Storage(S3Boto3Storage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        self.local_storage._save(name, content)
        super().save(name, self.local_storage._open(name))
        return name
