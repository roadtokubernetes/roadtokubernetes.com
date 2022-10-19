from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django_htmx.http import (HttpResponseClientRedirect,
                              HttpResponseClientRefresh)

from .context_processors import projects_context
from .forms import ProjectForm
from .models import Project


def projects_choices_view(request):
    user = request.user
    if not request.htmx:
        return render(request, "400.html", status=400)
    if not user.is_authenticated:
        return render(request, "hx/login-required.html", status=400)
    queryset = Project.objects.filter(user=request.user)
    if request.method == "POST":
        if 'project_id' in request.POST:
            """
            Current project was updated
            """
            project_id = request.POST.get('project_id')
            if project_id == "create":
                url_options = projects_context(request)
                return HttpResponseClientRedirect(url_options['projects_create_url'])
            qs_exists = queryset.filter(project_id=project_id).exists()
            if qs_exists:
                request.session['project_id'] = project_id
                # console_url = cfehome_urls(request)['console_url']
                # return HttpResponseClientRedirect(console_url)
                return HttpResponseClientRefresh()
    queryset = queryset[:10]
    return render(request, "projects/snippets/project_choices.html", {"object_list": queryset})


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
