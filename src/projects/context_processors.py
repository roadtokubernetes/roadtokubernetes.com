from django_hosts.resolvers import reverse as hosts_reverse


def projects_context(*args, **kwargs):
    return {
        "projects_choices_url": hosts_reverse("projects:choices", host='console'),
        "projects_list_url": hosts_reverse("projects:list", host='console'),
        "projects_create_url": hosts_reverse("projects:create", host='console'),
        "projects_select_url": hosts_reverse("projects:select", host='console'),

    }
