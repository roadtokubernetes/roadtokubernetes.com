"""cfehome URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView

from articles import views as articles_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    re_path(r"^signup/?", RedirectView.as_view(url="/account/signup/")),
    re_path(r"^sign-up/?", RedirectView.as_view(url="/account/signup/")),
    re_path(r"^join/?", RedirectView.as_view(url="/account/signup/")),
    re_path(r"^signin/?", RedirectView.as_view(url="/account/login/")),
    re_path(r"^sign-in/?", RedirectView.as_view(url="/account/login/")),
    re_path(r"^login/?", RedirectView.as_view(url="/account/login/")),
    re_path(r"^logout/?", RedirectView.as_view(url="/account/logout/")),
    re_path(r"^password-reset/?", RedirectView.as_view(url="/account/password/reset/")),
    re_path(r"^password/reset/?", RedirectView.as_view(url="/account/password/reset/")),
    path("account/", include("allauth.urls")),
    path("blog", RedirectView.as_view(url="/blog/")),
    path("blog/", include("articles.urls")),
    path("search", RedirectView.as_view(url="/search/")),
    path("search/", articles_views.SearchView.as_view(), name="search"),
    path("u/", include("profiles.urls")),
    path(
        "generator/",
        TemplateView.as_view(template_name="coming-soon.html"),
        name="generator",
    ),
    path("admin/", admin.site.urls),
    path(
        "secrets-encoder",
        TemplateView.as_view(template_name="utils/secrets-encoder.html"),
        name="secrets-encoder",
    ),
    path("webhooks/blog/", include("gh.webhooks")),
]


urlpatterns += [
    path("about/", flatpages_views.flatpage, {"url": "/about/"}, name="about"),
    path("contact/", flatpages_views.flatpage, {"url": "/contact/"}, name="contact"),
    path("sponsors/", flatpages_views.flatpage, {"url": "/sponsors/"}, name="sponsors"),
    path("privacy/", flatpages_views.flatpage, {"url": "/privacy/"}, name="privacy"),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("healthz", views.index),
    # path("<path:resource>", TemplateView.as_view(template_name="coming-soon.html")),
]
