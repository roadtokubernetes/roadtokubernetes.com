from django.conf import settings
from django_hosts.resolvers import reverse as hosts_reverse


def cfehome_urls(request):
    return {
        "console_url": hosts_reverse("index", host="console"),
        "root_url": hosts_reverse("index", host="www"),
        "blog_url": hosts_reverse("articles:article-list", host="www"),
        "search_url": hosts_reverse("search", host="www"),
        "secrets_encoder_url": hosts_reverse("secrets-encoder", host="www"),
        "generator_url": hosts_reverse("generator", host="www"),
    }
