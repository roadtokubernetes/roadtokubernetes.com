from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from . import views

app_name = "console"

urlpatterns = [
    path("", views.console_view, name="index"),
    path("apps/", include("apps.urls")),
    path("account/", include("allauth.urls")),
    path("projects/", include("projects.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
