from django.urls import path

from . import views

app_name = "apps"
urlpatterns = [
    path("", views.apps_list_view, name="list"),
    path("create/", views.apps_create_view, name="create"),
    path("env/key/validate/", views.apps_env_validate_key, name="validate-env-key"),
    path("pk/<uuid:pk>/", views.apps_detail_backup_view, name="detail-backup"),
    path("<slug:app_id>/env/", views.apps_env_view, name="env"),
    path("<slug:app_id>/secrets/", views.apps_secrets_view, name="secrets"),
    path("<slug:app_id>/inputs/", views.apps_new_input_view, name="inputs"),
    path("<slug:app_id>/download/", views.apps_manifest_download_view, name="download"),
    path("<slug:app_id>/", views.apps_detail_view, name="detail"),
    # path("<uuid:pk>/env/", views.apps_env_view, name="env"),
    # path("<uuid:pk>/secrets/", views.apps_secrets_view, name="secrets"),
    # path("<uuid:pk>/inputs/", views.apps_new_input_view, name="inputs"),
    # path("<uuid:pk>/download/", views.apps_manifest_download_view, name="download"),
]
