import base64
import uuid

from django.conf import settings
from django.db import models
from django.db.models import F
from django.template.loader import render_to_string
from django.utils.text import slugify
from django_hosts.resolvers import reverse as hosts_reverse

from cfehome.utils import yaml_loader
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
    name = models.CharField(
        max_length=120,
    )
    app_id = models.SlugField(blank=True, null=True)
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
    tls_secret_name = models.CharField(max_length=120, null=True, blank=True)
    custom_domain_names = models.TextField(
        null=True, blank=True, help_text="Separate domains by comma"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "name")

    def save(self, *args, **kwargs):
        if not self.namespace:
            self.namespace = "apps"
        self.app_id = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def display_label(self):
        return f"{self.title}"

    @property
    def title(self):
        if self.name:
            return self.name
        return self.container

    def get_absolute_url(self):
        if not self.app_id:
            return hosts_reverse(
                "apps:detail-backup", kwargs={"pk": self.pk}, host="console"
            )
        return hosts_reverse(
            "apps:detail", kwargs={"app_id": self.app_id}, host="console"
        )

    def get_inputs_url(self):
        return hosts_reverse(
            "apps:inputs", kwargs={"app_id": self.app_id}, host="console"
        )

    def get_secrets_url(self):
        return hosts_reverse(
            "apps:secrets", kwargs={"app_id": self.app_id}, host="console"
        )

    def get_env_url(self):
        return hosts_reverse("apps:env", kwargs={"app_id": self.app_id}, host="console")

    def get_download_url(self):
        return hosts_reverse(
            "apps:download", kwargs={"app_id": self.app_id}, host="console"
        )

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
    def secrets_label(self):
        return f"{self.k8s_label}-secret"

    @property
    def has_database(self):
        return self.database != DatabaseChoices.EMPTY

    @property
    def _namespace(self):
        return self.namespace or "apps"

    def get_secret_variables(self):
        qs = (
            self.appvariable_set.all()
            .filter(type=AppVariableChoices.SECRET)
            .exclude(key__iexact="PORT")
            .annotate(name=F("key"))
            .values_list("name", "value_encoded")
        )
        if not qs.exists():
            return {}, False
        qs = list(qs)
        data = {f"{x[0]}": f"{x[1]}" for x in qs}
        return data, True

    def get_container_environment_variables(self):
        qs = list(
            self.appvariable_set.all()
            .filter(type=AppVariableChoices.ENV)
            .exclude(key__iexact="PORT")
            .annotate(name=F("key"))
            .values("name", "value")
        )
        envs = qs + [{"name": "PORT", "value": self.container_port}]
        envs = sorted(envs, key=lambda x: x["name"])
        return envs

    def get_container_ports(self):
        return [
            {
                "name": f"{self.container_port_label}",
                "containerPort": int(self.container_port),
            }
        ]

    def get_domain_names(self):
        domains = self.custom_domain_names
        if domains == "" or domains is None:
            return []
        domains = [x.strip() for x in domains.split(",")]
        return domains

    def get_container_details(self, container_secrets=[]):
        return {
            "name": self.container_label,
            "image": self.container,
            "imagePullPolicy": self.image_pull_policy,
            "envFrom": container_secrets,
            "env": self.get_container_environment_variables(),
            "ports": self.get_container_ports(),
        }

    def get_manifests(self, as_dict=False):
        secrets_data, secrets_exist = self.get_secret_variables()
        container_secrets = []
        if secrets_exist:
            container_secrets.append({"secretRef": {"name": self.secrets_label}})
        container_details = self.get_container_details(
            container_secrets=container_secrets
        )
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
                tls_secret_name=self.tls_secret_name,
            )
            manifest_docs.append(ingress_yaml)

        secret_yaml = ""
        if secrets_exist:
            secret_yaml = renderers.get_secrets_manifest(
                name=self.secrets_label,
                namespace=self._namespace,
                data=secrets_data,
            )
            manifest_docs.append(secret_yaml)

        if as_dict:
            manifest_data = {
                "namespace": yaml_loader.load(namespace_yaml),
                "deployment": yaml_loader.load(deployment_yaml),
                "service": yaml_loader.load(service_yaml),
            }
            if ingress_yaml is not None:
                manifest_data["ingress"] = yaml_loader.load(ingress_yaml)
            if secrets_exist:
                manifest_data["secret"] = yaml_loader.load(secret_yaml)
            return manifest_data
        doc = "\n\n---\n".join(manifest_docs)
        return doc.strip()

    def get_manifests_markdown(self):
        manifests = self.get_manifests()
        return render_to_string("manifests/manifests.md", {"manifests": manifests})


class AppVariableChoices(models.TextChoices):
    ENV = "env", "Environment Variable"
    SECRET = "secret", "Secret"


class AppVariable(models.Model):
    app = models.ForeignKey(App, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    key = models.CharField(max_length=50)
    value = models.TextField()
    value_encoded = models.TextField(blank=True, null=True)
    encrypt = models.BooleanField(default=False)
    type = models.CharField(
        max_length=20,
        default=AppVariableChoices.ENV,
        choices=AppVariableChoices.choices,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key", "value"]

    @property
    def encoded(self):
        if not self.value_encoded:
            return None
        return self.value_encoded

    def save(self, *args, **kwargs):
        self.key = slugify(self.key).replace("-", "_").upper()
        if self.value and self.type == AppVariableChoices.SECRET:
            val_b = f"{self.value}".encode("utf-8")
            self.value_encoded = str(base64.b64encode(val_b).decode("utf-8"))
        super().save(*args, **kwargs)


class AppEnvVariable(AppVariable):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = AppVariableChoices.ENV
        super().save(*args, **kwargs)


class AppSecretVariable(AppVariable):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = AppVariableChoices.SECRET
        super().save(*args, **kwargs)
