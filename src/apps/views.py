from statistics import quantiles

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import CreateView, ListView, UpdateView
from django_htmx.http import HttpResponseClientRefresh

from projects.models import Project

from . import utils
from .forms import AppModelForm, AppModelUpdateForm
from .models import App, AppVariable, AppVariableChoices


class AppCreateFormView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = "apps/create.html"
    form_class = AppModelForm
    # success_url = "/apps/create/"
    success_message = "App created"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

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


class AppsListView(SuccessMessageMixin, LoginRequiredMixin, ListView):
    template_name = "apps/list.html"

    def get_queryset(self):
        project_id = self.request.session.get("project_id")
        if project_id:
            return App.objects.filter(project__project_id=project_id)
        return App.objects.filter(user=self.request.user)


apps_list_view = AppsListView.as_view()


class AppsDetailView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = "apps/update.html"
    form_class = AppModelUpdateForm
    success_message = "%(name)s was updated successfully"
    slug_field = "app_id"
    slug_url_kwarg = "app_id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context["object"]
        if obj:
            context["manifests"] = obj.get_manifests_markdown()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["app_editing"] = False
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        self.request.session["app_editing"] = True
        return response

    def get_queryset(self):
        project_id = self.request.session.get("project_id")
        if project_id:
            return App.objects.filter(project__project_id=project_id)
        return App.objects.filter(user=self.request.user)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        if "project" in form.fields:
            form.fields["project"].queryset = Project.objects.filter(
                user=self.request.user
            )
        return form


apps_detail_view = AppsDetailView.as_view()


apps_detail_backup_view = AppsDetailView.as_view()


def apps_manifest_download_view(request, app_id=None):
    if not request.user.is_authenticated:
        return HttpResponse("Please login", status=400)
    app = App.objects.filter(app_id=app_id, user=request.user).first()
    if not app:
        raise Http404
    response = HttpResponse(app.get_manifests(), content_type="text/plain")
    response["Content-Disposition"] = f"attachment; filename={app.k8s_label}.yaml"
    return response


def apps_env_validate_key(request):
    if request.method == "POST":
        data = dict(request.POST)
        for key, value in data.items():
            if "name" in key:
                for val in value:
                    if utils.check_password_name(val):
                        msg = "Passwords/secrets are not encrypted or stored safely here. Consider using placeholders."
                        return render(
                            request,
                            "apps/snippets/validation-warning.html",
                            {"msg": msg},
                        )
                    if val == "PORT" or val == "port":
                        msg = "PORT is mapped to the App Container Port and cannot be changed here."
                        return render(
                            request,
                            "apps/snippets/validation-warning.html",
                            {"msg": msg},
                        )
    return HttpResponse("")


def apps_new_input_view(request, app_id=None, *args, **kwargs):
    if not request.htmx:
        return HttpResponseBadRequest()
    return render(request, "apps/snippets/inputs.html", {})


def apps_env_view(request, app_id=None):
    if not request.htmx:
        return HttpResponseBadRequest()
    if not request.user.is_authenticated:
        return HttpResponse("Please login", status=400)

    qs = AppVariable.objects.filter(
        app__app_id=app_id, app__user=request.user, type=AppVariableChoices.ENV
    )
    if request.method == "POST":
        qs.delete()
        data = dict.copy(request.POST)
        keys = data.get("name")
        values = data.get("value")
        new_vars = []
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(values, list):
            values = [values]
        for i, k in enumerate(zip(keys, values)):
            if len(k) == 2 and all(k):
                _key = slugify(k[0]).replace("-", "_")
                _key = f"{_key}".upper()
                new_var = AppVariable.objects.create(
                    app_id=app_id,
                    user=request.user,
                    key=_key,
                    value=k[1],
                    type=AppVariableChoices.ENV,
                )
                new_vars.append(new_var.id)
        messages.success(request, "Environment variables have been updated.")
        return HttpResponseClientRefresh()
        # qs = AppVariable.objects.filter(id__in=new_vars)
    return render(request, "apps/snippets/input_datas.html", {"object_list": qs})


def apps_secrets_view(request, app_id=None):
    if not request.htmx:
        return HttpResponseBadRequest()
    if not request.user.is_authenticated:
        return HttpResponse("Please login", status=400)
    qs = AppVariable.objects.filter(
        app__app_id=app_id, app__user=request.user, type=AppVariableChoices.SECRET
    )
    if request.method == "POST":
        qs.delete()
        data = dict.copy(request.POST)
        keys = data.get("name")
        values = data.get("value")
        new_vars = []
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(values, list):
            values = [values]
        for i, k in enumerate(zip(keys, values)):
            if len(k) == 2 and all(k):
                _key = slugify(k[0]).replace("-", "_")
                _key = f"{_key}".upper()
                new_var = AppVariable.objects.create(
                    app_id=app_id,
                    user=request.user,
                    key=_key,
                    value=k[1],
                    type=AppVariableChoices.SECRET,
                )
                new_vars.append(new_var.id)
        messages.success(request, "App secrets have been updated.")
        return HttpResponseClientRefresh()
        # qs = AppVariable.objects.filter(id__in=new_vars)
    return render(request, "apps/snippets/input_datas.html", {"object_list": qs})
