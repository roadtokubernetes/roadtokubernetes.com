from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView
from projects.models import Project

from .forms import AppModelForm, AppModelUpdateForm
from .models import App


class AppCreateFormView(SuccessMessageMixin, CreateView):
    template_name = "apps/create.html"
    form_class = AppModelForm
    # success_url = "/apps/create/"
    success_message = "App created"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        project_id = self.request.session.get("project_id")
        project_qs = Project.objects.filter(
            user=self.request.user, project_id=project_id
        )
        if project_qs.exists():
            obj.project = project_qs.first()
        obj.save()
        return super().form_valid(form)


apps_create_view = AppCreateFormView.as_view()


class AppsListView(SuccessMessageMixin, ListView):
    template_name = "apps/list.html"

    def get_queryset(self):
        project_id = self.request.session.get("project_id")
        if project_id:
            return App.objects.filter(project__project_id=project_id)
        return App.objects.filter(user=self.request.user)


apps_list_view = AppsListView.as_view()


class AppsDetailView(SuccessMessageMixin, UpdateView):
    template_name = "apps/update.html"
    form_class = AppModelUpdateForm
    success_message = "%(label)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context["object"]
        if obj:
            context["manifests"] = obj.get_manifests_markdown()
        return context

    def get_queryset(self):
        project_id = self.request.session.get("project_id")
        if project_id:
            return App.objects.filter(project__project_id=project_id)
        return App.objects.filter(user=self.request.user)


apps_detail_view = AppsDetailView.as_view()

# Create your views here.
def apps_create_view2(request):
    form = AppModelForm()
    return render(request, "apps/create.html", {"form": form})
