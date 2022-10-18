from django.conf import settings


def console_url(request):
    return {
        "console_url": settings.CONSOLE_URL
    }
