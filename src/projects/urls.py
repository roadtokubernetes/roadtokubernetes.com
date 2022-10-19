from django.urls import path

from . import views

app_name='projects'
urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
     path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<slug:project_id>/', views.ProjectDetailView.as_view(), name='detail')
]
