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
    database = forms.ChoiceField(
        widget=forms.Select,
        label="Database (optional)",
        help_text="This will unlock a k8s configuration for a database",
        initial=DatabaseChoices.EMPTY,
        choices=DB_CHOICES,
        required=True,
    )
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
            "database",
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
        return names


class AppCreateForm(forms.Form):
    label = forms.CharField()
    container = forms.CharField(
        initial="nginx",
        help_text="Since Kubernetes runs containers, this is where we must start.",
    )
    container_port = forms.CharField(initial="8000", required=True)
    database = forms.ChoiceField(
        widget=forms.Select,
        label="Database (optional)",
        choices=DatabaseChoices.choices,
        required=False,
    )
    allow_internet_traffic = forms.ChoiceField(
        widget=forms.Select,
        label="Allow Internet Traffic (optional)",
        choices=ExternalIngressChoices.choices,
        initial=ExternalIngressChoices.ENABLE,
        required=True,
    )
    custom_domain_names = forms.CharField(
        required=False, help_text="Separate domains by comma"
    )
    # label = forms.CharField(required=False)
    # description = forms.CharField(required=False)

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
        return names
