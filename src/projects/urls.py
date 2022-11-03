from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("create/", views.ProjectCreateView.as_view(), name="create"),
    path("choices/", views.projects_choices_view, name="choices"),
    path("select/", views.projects_choices_view, name="select"),
    path("<slug:project_id>/delete/", views.project_delete_view, name="delete"),
    path("<slug:project_id>/", views.ProjectDetailView.as_view(), name="detail"),
]
