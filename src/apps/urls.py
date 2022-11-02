from django.urls import path

from . import views

app_name = "apps"
urlpatterns = [
    path("", views.apps_list_view, name="list"),
    path("create/", views.apps_create_view, name="create"),
    path("env/key/validate/", views.apps_env_validate_key, name="validate-env-key"),
    path("<uuid:pk>/env/", views.apps_env_view, name="env"),
    path("<uuid:pk>/secrets/", views.apps_secrets_view, name="secrets"),
    path("<uuid:pk>/inputs/", views.apps_new_input_view, name="inputs"),
    path("<uuid:pk>/", views.apps_detail_view, name="detail"),
]
