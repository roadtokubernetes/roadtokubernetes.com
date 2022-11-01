from django.urls import path

from . import views

app_name = "apps"
urlpatterns = [
    path("", views.apps_list_view, name="list"),
    path("create/", views.apps_create_view, name="create"),
    path("<uuid:pk>/", views.apps_detail_view, name="detail"),
]
