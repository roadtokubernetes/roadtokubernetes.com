from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django_hosts.resolvers import reverse as hosts_reverse

from . import utils

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=utils.get_profile_image_upload_to, blank=True, null=True
    )
    title = models.CharField(max_length=120, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username}"

    @property
    def username(self):
        return self.user.username

    def get_full_name(self):
        return self.user.get_full_name()

    @property
    def name(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return hosts_reverse(
            "profiles:detail",
            host="www",
            kwargs={"username": self.username},
        )


def user_post_save(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(user_post_save, sender=User)
