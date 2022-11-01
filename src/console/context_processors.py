from django.conf import settings
from django_hosts.resolvers import reverse as hosts_reverse


def console_url(request):
    return {"console_url": settings.CONSOLE_URL}


def console_context(*args, **kwargs):
    return {
        "apps_create_url": hosts_reverse("apps:create", host="console"),
        "apps_list_url": hosts_reverse("apps:list", host="console"),
        "projects_choices_url": hosts_reverse("projects:choices", host="console"),
        "projects_list_url": hosts_reverse("projects:list", host="console"),
        "projects_create_url": hosts_reverse("projects:create", host="console"),
        "projects_select_url": hosts_reverse("projects:select", host="console"),
    }
