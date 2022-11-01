import uuid

from cfehome.utils import yaml_loader
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify
from django_hosts.resolvers import reverse as hosts_reverse
from projects.models import Project

User = settings.AUTH_USER_MODEL

# Create your models here.
class DatabaseChoices(models.TextChoices):
    EMPTY = "na", "No database"
    PGSQL = "psql", "PostgreSQL"
    MYSQL = "mysql", "MySQL"
    MONGO = "mongo", "MongoDB"

    __empty__ = "Select database"


class ExternalIngressChoices(models.IntegerChoices):
    ENABLE = 1, "Enable"
    DISABLE = 0, "Disable"

    __empty__ = "Select to allow internet traffic:"


class App(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.SET_NULL
    )
    label = models.CharField(max_length=120, null=True, blank=True)
    container = models.TextField(null=True, blank=True, help_text="Include any tag")
    container_port = models.CharField(
        max_length=120, null=True, blank=True, default="8000"
    )
    database = models.CharField(
        max_length=120,
        choices=DatabaseChoices.choices,
        null=True,
        blank=True,
        default=DatabaseChoices.EMPTY,
    )
    allow_internet_traffic = models.IntegerField(
        choices=ExternalIngressChoices.choices,
        default=ExternalIngressChoices.ENABLE,
        null=True,
        blank=True,
    )
    custom_domain_names = models.TextField(
        null=True, blank=True, help_text="Separate domains by comma"
    )

    def __str__(self):
        return self.title

    @property
    def display_label(self):
        return f"{self.title}"

    @property
    def title(self):
        if self.label:
            return self.label
        return self.container

    def get_absolute_url(self):
        return hosts_reverse("apps:detail", kwargs={"pk": self.uuid}, host="console")

    @property
    def k8s_label(self):
        return slugify(f"{self.title}")

    @property
    def deployment_label(self):
        return f"{self.k8s_label}-dp"

    @property
    def service_type(self):
        return "ClusterIP"

    @property
    def service_label(self):
        return f"{self.k8s_label}-srv"

    @property
    def container_label(self):
        return f"{self.k8s_label}-container"

    @property
    def container_port_label(self):
        return f"{self.k8s_label}-cp"

    def get_container_environment_variables(self):
        return [{"name": "PORT", "value": self.container_port}]

    def get_container_ports(self):
        return [
            {"name": f"{self.container_port_label}", "value": int(self.container_port)}
        ]

    def get_container_details(self):
        return {
            "name": self.container_label,
            "image": self.container,
            "imagePullPolicy": "Always",
            "envFrom": [],
            "env": self.get_container_environment_variables(),
            "ports": self.get_container_ports(),
        }

    def get_manifests(self):
        container_details = self.get_container_details()
        containers = [container_details]
        namespace = "apps"

        deployment_data = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"namespace": f"{namespace}", "name": self.deployment_label},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": self.deployment_label}},
            },
            "template": {
                "metadata": {"labels": {"app": self.deployment_label}},
                "spec": {"containers": containers},
            },
        }
        service_type = "ClusterIP"
        ports = [
            {
                "name": "http",
                "protocol": "TCP",
                "port": 80,
                "targetPort": self.container_port_label,
            }
        ]
        service_data = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"namespace": f"{namespace}", "label": self.service_label},
            "spec": {
                "type": service_type,
                "ports": ports,
                "selector": self.deployment_label,
            },
        }
        deployment_yaml = yaml_loader.dump(deployment_data).strip()
        service_yaml = yaml_loader.dump(service_data).strip()
        service_yaml = f"\n---\n{service_yaml}"
        doc = """{deployment_yaml} {service_yaml}
        """.format(
            deployment_yaml=deployment_yaml, service_yaml=service_yaml
        )
        return doc.strip()

    def get_manifests_markdown(self):
        manifests = self.get_manifests()
        return render_to_string("manifests/manifests.md", {"manifests": manifests})
