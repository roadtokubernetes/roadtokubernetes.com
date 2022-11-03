from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.utils.text import slugify

from projects.models import Project

from .models import App, ExternalIngressChoices

FIXTURES_DIR = getattr(settings, "FIXTURES_DIR") or (settings.BASE_DIR / "fixtures")

User = get_user_model()


@override_settings(DEFAULT_HOST="console")
class AppTestCase(TestCase):
    fixtures = [FIXTURES_DIR / "auth.json"]

    def setUp(self):
        self.user_a_username = "abc"
        self.user_a_password = "easy_password"
        user_a = User.objects.create(username=self.user_a_username)
        user_a.set_password(self.user_a_password)
        user_a.save()
        self.user_a = user_a
        self.project_a = Project.objects.create(
            user=self.user_a, name="Project A", project_id="project-a"
        )
        rf = RequestFactory()
        rf.defaults["SERVER_NAME"] = settings.PARENT_HOST

        self.client.login(username=self.user_a_username, password=self.user_a_password)
        session = self.client.session
        session["project_id"] = f"{self.project_a.project_id}"
        session.save()
        self.app_a = App.objects.create(
            name="Test App",
            project=self.project_a,
            container="nginx",
            container_port="8000",
            allow_internet_traffic=ExternalIngressChoices.DISABLE,
        )

    def test_app_slug(self):
        title = self.app_a.name
        app_id = self.app_a.app_id
        _app_id = slugify(title)
        self.assertEqual(app_id, _app_id)

    def test_auth(self):
        response = self.client.get("/account/email/")
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        response = self.client.get(f"/apps/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "apps/list.html")

    def test_detail_view(self):
        response = self.client.get(f"/apps/{self.app_a.app_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "apps/update.html")
