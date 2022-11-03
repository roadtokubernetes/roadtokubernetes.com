import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.generic import CreateView, ListView, UpdateView, View
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh

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


def apps_rk8s_raw_view(request, app_id=None):
    if not request.user.is_authenticated:
        return HttpResponse("Please login", status=400)
    project_id = request.session.get("project_id")
    obj = App.objects.filter(app_id=app_id, project__project_id=project_id).first()
    if not obj:
        return JsonResponse({}, status=404)
    data = obj.serialize()
    if request.htmx:
        data = json.dumps(data, indent=4)
        content = render_to_string(
            "markdown/code-block.txt", {"content": data, "lang": "json"}
        )
        return render(request, "markdown/markdown-block.html", {"content": content})
    return JsonResponse(data)


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


class AppVariableView(View):
    type = AppVariableChoices.ENV
    model = AppVariable
    success_message = "Environment variables have been updated."

    def get_queryset(self):
        return self.model.objects.filter(
            type=self.type,
            app__app_id=self.kwargs.get("app_id"),
            app__user=self.request.user,
        )

    def get_app(self):
        return App.objects.filter(
            app_id=self.kwargs.get("app_id"),
            project__project_id=self.request.session.get("project_id"),
        ).first()

    def get(self, request, *args, **kwargs):
        if not request.htmx:
            return HttpResponseBadRequest()
        if not request.user.is_authenticated:
            return HttpResponse("Please login", status=400)
        qs = self.get_queryset()
        return render(request, "apps/snippets/input_datas.html", {"object_list": qs})

    def post(self, request, *args, **kwargs):
        if not request.htmx:
            return HttpResponseBadRequest()
        if not request.user.is_authenticated:
            return HttpResponse("Please login", status=400)
        qs = self.get_queryset()
        qs.delete()
        app = self.get_app()
        data = dict.copy(request.POST)
        keys = data.get("name")
        values = data.get("value")
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(values, list):
            values = [values]
        for i, k in enumerate(zip(keys, values)):
            if len(k) == 2 and all(k):
                _key = slugify(k[0]).replace("-", "_")
                _key = f"{_key}".upper()
                AppVariable.objects.create(
                    app=app,
                    user=request.user,
                    key=_key,
                    value=k[1],
                    type=self.type,
                )
        messages.success(request, self.success_message)
        return HttpResponseClientRefresh()


class AppEnvView(AppVariableView):
    type = AppVariableChoices.ENV
    success_message = "Environment variables have been updated."


apps_env_view = AppEnvView.as_view()


class AppSecretView(AppVariableView):
    type = AppVariableChoices.SECRET
    success_message = "Secrets have been updated."


apps_secrets_view = AppSecretView.as_view()


def app_delete_view(request, app_id):
    if not request.htmx:
        return HttpResponseBadRequest()
    if not request.user.is_authenticated:
        return HttpResponse("Please login", status=400)
    project_id = request.session.get("project_id")
    if request.method == "DELETE":
        obj = App.objects.filter(app_id=app_id, project__project_id=project_id).first()
        if not obj:
            messages.error(request, "App is missing or no longer exists.")
            return HttpResponseClientRedirect("/apps/")
        obj.delete()
        return HttpResponseClientRedirect("/apps/")
    return HttpResponse("Not allowed", status=400)
