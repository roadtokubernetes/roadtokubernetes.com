from django import forms
from django.conf import settings
from django.utils.text import slugify

from . import validators
from .models import App, DatabaseChoices, ExternalIngressChoices

BASE_URL = settings.BASE_URL
DB_CHOICES = DatabaseChoices.choices

EXTERNAL_TRAFFIC_CHOICES = ExternalIngressChoices.choices


class AppModelForm(forms.ModelForm):
    container = forms.CharField(
        initial="nginx",
        help_text="Since Kubernetes runs containers, this is where we must start.",
    )
    container_port = forms.CharField(initial="8000", required=True)
    # database = forms.ChoiceField(
    #     widget=forms.Select,
    #     label="Database (optional)",
    #     help_text="This will unlock a k8s configuration for a database",
    #     initial=DatabaseChoices.EMPTY,
    #     choices=DB_CHOICES,
    #     required=True,
    # )
    allow_internet_traffic = forms.ChoiceField(
        widget=forms.Select,
        label="Allow Internet Traffic",
        choices=EXTERNAL_TRAFFIC_CHOICES,
        initial=ExternalIngressChoices.DISABLE,
        required=True,
    )
    custom_domain_names = forms.CharField(
        required=False, help_text="Separate domains by comma"
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    class Meta:
        model = App
        fields = [
            "name",
            "container",
            "container_port",
            # "database",
            "allow_internet_traffic",
            "custom_domain_names",
        ]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("An app name is required")
        if self.instance:
            """
            Instance exists.
            """
            if self.instance.name == name:
                """instance name did not change
                return original name"""
                return name
        qs = App.objects.filter(
            project__project_id=self.request.session.get("project_id"),
        )
        qs1 = qs.filter(name__iexact=name)
        if qs1.exists():
            raise forms.ValidationError(f"{name} already exists for this project.")
        slug_name = slugify(name)
        qs2 = qs.filter(app_id__iexact=slug_name)
        if qs2.exists():
            raise forms.ValidationError(
                f"App id {slug_name} (from {name}) already exists for this project."
            )
        return name

    def clean_custom_domain_names(self):
        data = self.cleaned_data.get("custom_domain_names")
        if not data:
            return
        names = [x.strip() for x in data.split(",")]
        for _name in names:
            if _name.startswith("http"):
                try:
                    validators.url_validator(_name)
                except Exception as errors:
                    for e in errors:
                        self.add_error("custom_domain_names", f"{_name}: {e}")
            if not _name.startswith("http"):
                try:
                    validators.url_validator(f"http://{_name}")
                except Exception as errors:
                    for e in errors:
                        self.add_error("custom_domain_names", f"{_name}: {e} ")
        return ",".join(names)


class AppModelUpdateForm(AppModelForm):
    namespace = forms.SlugField(initial="apps", help_text="")
    # app_id = forms.SlugField(widget=forms.ReadOnlyInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    class Meta:
        model = App
        fields = [
            # "project",
            "name",
            "app_id",
            "namespace",
            "container",
            "container_port",
            "image_pull_policy",
            "replicas",
            # "database",
            "allow_internet_traffic",
            "custom_domain_names",
            "tls_secret_name",
        ]
        labels = {"tls_secret_name": "TLS Secret Name"}
        help_texts = {
            "container": "Only public images are supported at this time",
            "image_pull_policy": "Select how often kubernetes should pull this image. Default: Always",
            "replicas": "Number of times Kubernetes should have this running.",
            "tls_secret_name": f"TLS secret name for generating the TLS certs. <a class='underline text-blue-700' href='{BASE_URL}/blog/tls'>Learn more</a>",
            "app_id": "The app id that will be used in the URL. It is auto-generated from the app name.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image_pull_policy"].widget.attrs.update({"class": "mb-0"})
        self.fields["app_id"].widget.attrs.update({"readonly": True, "disabled": True})
