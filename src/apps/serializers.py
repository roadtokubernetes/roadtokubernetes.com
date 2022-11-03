from rest_framework import serializers

from .models import App


class AppRawSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField(source="project.project_id", read_only=True)
    allow_internet_traffic = serializers.BooleanField()
    environment_variables = serializers.SerializerMethodField(read_only=True)
    secrets = serializers.SerializerMethodField(read_only=True)
    domain_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = App
        fields = sorted(
            [
                "app_id",
                "project_id",
                "name",
                "container",
                "container_port",
                "image_pull_policy",
                "allow_internet_traffic",
                "tls_secret_name",
                "domain_names",
                "environment_variables",
                "secrets",
            ]
        )

    def get_environment_variables(self, obj):
        return obj.get_container_environment_variables()

    def get_secrets(self, obj):
        secrets, exists = obj.get_secret_variables()
        if not exists:
            return None
        return secrets

    def get_domain_names(self, obj):
        return obj.get_domain_names()
