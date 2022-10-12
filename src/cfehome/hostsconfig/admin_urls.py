from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", admin.site.urls),
]

DEBUG_TOOLBAR = getattr(settings, 'DEBUG_TOOLBAR', None)

if str(DEBUG_TOOLBAR) == "1":
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
