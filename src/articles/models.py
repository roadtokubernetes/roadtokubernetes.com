import markdown
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.html import strip_tags
from django_hosts.resolvers import reverse as hosts_reverse
from gh.client import ArticleMapper

from . import utils

User = settings.AUTH_USER_MODEL  # defaults to 'auth.User'


class ArticleQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(publish_status=Article.ArticlePublishOptions.PUBLISH).filter(
            Q(publish_timestamp__lte=now) | Q(user_publish_timestamp__lte=now)
        )

    def pending_published(self):
        now = timezone.now()
        return self.filter(publish_status=Article.ArticlePublishOptions.PUBLISH).filter(
            Q(publish_timestamp__gt=now) | Q(user_publish_timestamp__gt=now)
        )

    def drafts(self):
        return self.filter(publish_status=Article.ArticlePublishOptions.DRAFT)

    def select_author(self):
        return self.select_related("user")

    def search(self, query=None):
        if query is None:
            return self.none()
        return self.filter(Q(title__icontains=query) | Q(content__icontains=query))


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published().select_author()

    def drafts(self):
        return self.get_queryset().drafts().select_author()

    def pending(self):
        return self.get_queryset().pending_published().select_author()


class Article(models.Model):
    class ArticlePublishOptions(models.TextChoices):
        PUBLISH = "pub", "Publish"
        DRAFT = "dra", "DRAFT"
        PRIVATE = "pri", "Private"

    user = models.ForeignKey(User, default=1, on_delete=models.SET_DEFAULT)
    updated_by = models.ForeignKey(
        User, related_name="editor", null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    summary = models.CharField(max_length=220, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_title = models.CharField(max_length=120, blank=True, null=True)
    image = models.ImageField(
        upload_to=utils.get_article_image_upload_to, null=True, blank=True
    )
    publish_status = models.CharField(
        max_length=3,
        choices=ArticlePublishOptions.choices,
        default=ArticlePublishOptions.DRAFT,
    )
    publish_timestamp = models.DateTimeField(
        help_text="Field-driven publish timestamp",
        auto_now_add=False,
        auto_now=False,
        blank=True,
        null=True,
    )
    user_publish_timestamp = models.DateTimeField(
        help_text="User-defined publish timestamp",
        auto_now_add=False,
        auto_now=False,
        blank=True,
        null=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ArticleManager()

    class Meta:
        ordering = ["-user_publish_timestamp", "-publish_timestamp", "-updated"]

    def get_absolute_url(self):
        return hosts_reverse("articles:article-detail", kwargs={"slug": self.slug},host="www")

    def get_host_url(self):
        if settings.DEBUG:
            path = hosts_reverse("articles:article-detail", kwargs={"slug": self.slug},host="www")
            return path.replace(settings.BASE_URL, settings.PROD_URL)
        return hosts_reverse("articles:article-detail", kwargs={"slug": self.slug}, host="www")

    def get_image_url(self):
        if not self.image:
            return None
        return self.image.url

    def get_meta_description(self):
        return self.meta_description if self.meta_description else self.title
    
    @property
    def author(self):
        return self.user

    @property
    def author_name(self):
        try:
            return self.author.get_full_name()
        except:
            return None

    @property
    def is_published(self):
        if not self.publish_status == Article.ArticlePublishOptions.PUBLISH:
            return False
        now = timezone.now()
        if self.user_publish_timestamp is not None:
            return self.user_publish_timestamp <= now
        return self.publish_timestamp <= now

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = utils.unique_slug_generator(self)
        if self.user_publish_timestamp:
            """
            User has set user_publish_timestamp,
            Automatically set publish_timestamp
            """
            self.publish_timestamp = self.user_publish_timestamp
        if self.publish_status == Article.ArticlePublishOptions.PUBLISH:
            """
            User has set publish_status to PUBLISH,
            Automatically set publish_timestamp to
            now
            """
            if not self.publish_timestamp:
                self.publish_timestamp = timezone.now()
        if self.content and not self.summary:
            content_marked = markdown.markdown(self.content)
            content_stripped = strip_tags(content_marked)
            content_trunc = truncatechars(content_stripped, 220)
            self.summary = utils.strip_string_formatting(content_trunc)
        if self.content and not self.meta_description:
            content_marked = markdown.markdown(self.content)
            content_stripped = strip_tags(content_marked)
            meta_description_trunc = truncatechars(content_stripped, 160)
            self.meta_description = utils.strip_string_formatting(meta_description_trunc)
        if self.title and not self.meta_title:
            self.meta_title = truncatechars(self.title, 160)
        super().save(*args, **kwargs)



def article_post_save(sender, instance, *args, **kwargs):
    if instance.is_published:
        gh_mapper = ArticleMapper(
            slug=instance.slug,
            title=instance.title,
            author=instance.author_name,
            publish_timestamp=instance.publish_timestamp,
            content=instance.content,
            url=instance.get_host_url(),
        )
        gh_mapper.save()


post_save.connect(article_post_save, sender=Article)
