from rest_framework import serializers

from .models import App


class AppRawSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField(source="project.project_id", read_only=True)
    allow_internet_traffic = serializers.BooleanField()

    class Meta:
        model = App
        fields = [
            "app_id",
            "project_id",
            "name",
            "container",
            "container_port",
            "image_pull_policy",
            "allow_internet_traffic",
            "tls_secret_name",
            "custom_domain_names",
        ]
