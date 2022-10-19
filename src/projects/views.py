from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views import generic

from .forms import ProjectForm
from .models import Project


class ProjectDetailView(LoginRequiredMixin,SuccessMessageMixin, generic.UpdateView):
    slug_field = "project_id"
    slug_url_kwarg = "project_id"
    form_class = ProjectForm 
    template_name = "projects/project_update.html"
    success_message = "Updated successfully"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)



class ProjectListView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class ProjectCreateView(LoginRequiredMixin,SuccessMessageMixin, generic.CreateView):
    template_name = "projects/project_form.html"
    form_class = ProjectForm 
    success_message = "Project was successfully created."

    def form_valid(self, form):
        form.instance.user  = self.request.user
        form.save()
        return super().form_valid(form)

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)
