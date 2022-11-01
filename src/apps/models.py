import uuid

import yaml
from cfehome.utils import yaml_loader
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify
from django_hosts.resolvers import reverse as hosts_reverse
from projects.models import Project

from . import renderers, validators

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


class ImagePullPolicyChoices(models.TextChoices):
    ALWAYS = "Always", "Always"
    IF_NOT_PRESENT = "IfNotPresent", "If not already present"


class App(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.SET_NULL
    )
    label = models.CharField(max_length=120, null=True, blank=True)
    namespace = models.SlugField(null=True, blank=True)
    replicas = models.IntegerField(
        default=1, validators=[validators.validate_replica_count]
    )
    container = models.TextField(null=True, blank=True, help_text="Include any tag")
    container_port = models.CharField(
        max_length=120, null=True, blank=True, default="8000"
    )
    image_pull_policy = models.CharField(
        max_length=120,
        help_text="When should Kubernetes pull this image",
        choices=ImagePullPolicyChoices.choices,
        default=ImagePullPolicyChoices.ALWAYS,
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
    def service_port(self):
        return 80

    @property
    def service_label(self):
        return f"{self.k8s_label}-srv"

    @property
    def container_label(self):
        return f"{self.k8s_label}-container"

    @property
    def container_port_label(self):
        return f"{self.k8s_label}-cp"

    @property
    def ingress_label(self):
        return f"{self.k8s_label}-ingress"

    @property
    def has_database(self):
        return self.database is not DatabaseChoices.EMPTY

    @property
    def _namespace(self):
        return self.namespace or "apps"

    def get_container_environment_variables(self):
        return [{"name": "PORT", "value": self.container_port}]

    def get_container_ports(self):
        return [
            {"name": f"{self.container_port_label}", "value": int(self.container_port)}
        ]

    def get_domain_names(self):
        domains = self.custom_domain_names
        if domains is "" or domains is None:
            return []
        domains = [x.strip() for x in domains.split(",")]
        return domains

    def get_container_details(self):
        return {
            "name": self.container_label,
            "image": self.container,
            "imagePullPolicy": self.image_pull_policy,
            "envFrom": [],
            "env": self.get_container_environment_variables(),
            "ports": self.get_container_ports(),
        }

    def get_manifests(self, as_dict=False):
        container_details = self.get_container_details()
        containers = [container_details]

        deployment_yaml = renderers.get_deployment_manifest(
            name=self.deployment_label,
            namespace=self._namespace,
            replicas=self.replicas,
            containers=containers,
        )
        ports = [
            {
                "name": "http",
                "protocol": "TCP",
                "port": 80,
                "targetPort": self.container_port_label,
            }
        ]
        namespace_yaml = renderers.get_namespace_manifest(namespace=self._namespace)
        service_yaml = renderers.get_service_manifest(
            name=self.service_label,
            deployment_name=self.deployment_label,
            namespace=self._namespace,
            service_type=self.service_type,
            ports=ports,
        )
        manifest_docs = [namespace_yaml, deployment_yaml, service_yaml]
        ingress_yaml = None
        if self.allow_internet_traffic:
            domains = self.get_domain_names()
            ingress_yaml = renderers.get_ingress_manifest(
                domains=domains,
                namespace=self._namespace,
                name=self.ingress_label,
                service_name=self.service_label,
                service_port=self.service_port,
            )
            manifest_docs.append(ingress_yaml)
        if as_dict:
            manifest_data = {
                "namespace": yaml_loader.load(namespace_yaml),
                "deployment": yaml_loader.load(deployment_yaml),
                "service": yaml_loader.load(service_yaml),
            }
            if ingress_yaml is not None:
                manifest_data["ingress"] = yaml_loader.load(ingress_yaml)
            return manifest_data
        doc = "\n\n---\n".join(manifest_docs)
        return doc.strip()

    def get_manifests_markdown(self):
        manifests = self.get_manifests()
        return render_to_string("manifests/manifests.md", {"manifests": manifests})
