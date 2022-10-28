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
from articles import views as articles_views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView

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
    path("account/", include("allauth.urls")),
    path("blog", RedirectView.as_view(url="/blog/")),
    path("blog/", include("articles.urls")),
    path("search", RedirectView.as_view(url="/search/")),
    path("search/", articles_views.SearchView.as_view(), name="search"),
    path("u/", include("profiles.urls")),
    path("about/", TemplateView.as_view(template_name="coming-soon.html")),
    path("contact/", TemplateView.as_view(template_name="coming-soon.html")),
    path("generator/", TemplateView.as_view(template_name="coming-soon.html")),
    path("privacy/", TemplateView.as_view(template_name="coming-soon.html")),
    path("sponsors/", TemplateView.as_view(template_name="coming-soon.html")),
    path("admin/", admin.site.urls),
    path("webhooks/blog/", include("gh.webhooks")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("healthz", views.index),
    # path("<path:resource>", TemplateView.as_view(template_name="coming-soon.html")),
]
