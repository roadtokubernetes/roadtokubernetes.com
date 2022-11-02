from django import forms
from django.core.validators import URLValidator

from . import validators
from .models import App, DatabaseChoices, ExternalIngressChoices

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
        label="Allow Internet Traffic (optional)",
        choices=EXTERNAL_TRAFFIC_CHOICES,
        initial=ExternalIngressChoices.ENABLE,
        required=True,
    )
    custom_domain_names = forms.CharField(
        required=False, help_text="Separate domains by comma"
    )

    class Meta:
        model = App
        fields = [
            "label",
            "container",
            "container_port",
            # "database",
            "allow_internet_traffic",
            "custom_domain_names",
        ]

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

    class Meta:
        model = App
        fields = [
            # "project",
            "label",
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
            "tls_secret_name": "TLS secret name for generating the TLS certs.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image_pull_policy"].widget.attrs.update({"class": "mb-0"})
