from django.urls import path

from . import views

urlpatterns = [
    path("events/push/", views.handle_repo_event),
]
