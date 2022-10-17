import pathlib

from django.utils.text import slugify


def get_profile_image_upload_to(instance, filename):
    fpath = pathlib.Path(filename)
    slug = slugify(instance.username)
    return f"u/{slug}{fpath.suffix}"
