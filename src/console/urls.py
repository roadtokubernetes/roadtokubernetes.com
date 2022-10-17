from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from . import views

urlpatterns = [
    path("", views.console_view),

]
