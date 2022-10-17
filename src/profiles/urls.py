from django.urls import path

from . import views

app_name = "profiles"
urlpatterns = [
    path("<slug:username>/", views.ProfileView.as_view(), name="detail"),
]
