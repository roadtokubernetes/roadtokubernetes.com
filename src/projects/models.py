import uuid

from django.conf import settings
from django.db import models
from django_hosts.resolvers import reverse as hosts_reverse

from . import validators

User = settings.AUTH_USER_MODEL


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    project_id = models.SlugField(max_length=30, validators=[validators.valid_project_id], unique=True)
    label = models.CharField(max_length=120, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    timestamp  = models.DateTimeField(auto_now_add=True)
    updated  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_label

    def get_absolute_url(self):
        return hosts_reverse(
            "projects:detail",
            host="console",
            kwargs={"project_id": self.project_id},
        )

    @property
    def display_label(self):
        if self.label is not None:
            return f"{self.label}"
        return f"{self.project_id}" 
