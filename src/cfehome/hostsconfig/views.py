import os

from django.conf import settings
from django.http import HttpResponseRedirect

BASE_URL = getattr(settings, 'BASE_URL', None)
def homepage_redirect(request, path=None):
    url = f"{settings.PROD_URL}"
    if BASE_URL is not None:
        url = BASE_URL
    if not url.endswith("/"):
        url = f"{url}/"
    if path is not None:
        url = url + path
    return HttpResponseRedirect(url)
