from django.conf import settings
from django.contrib import admin
from django_hosts import host, patterns

DEFAULT_ADMIN_HOST = getattr(settings, "DEFAULT_ADMIN_HOST", "admin")
host_patterns = patterns(
    "",
    # host(r'v2', settings.ROOT_URLCONF, name='v1'),
    host(r"www", "cfehome.urls", name="www"),
    host(r"", "cfehome.urls", name="root"),
    host(DEFAULT_ADMIN_HOST, "cfehome.hostsconfig.admin_urls", name="admin"),
    # host(r"(?!www)\w+", "cfehome.hostsconfig.redirect_urls", name="wildcard"),
    # host(r'(\w+)', settings.ROOT_URLCONF, name='wildcard'),
)
