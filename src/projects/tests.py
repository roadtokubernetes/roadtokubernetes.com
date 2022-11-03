import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils.text import slugify

from cfehome import utils

from .models import Project

FIXTURES_DIR = getattr(settings, "FIXTURES_DIR") or (settings.BASE_DIR / "fixtures")

User = get_user_model()


@override_settings(DEFAULT_HOST="console")
class ProjectTestCase(TestCase):
    fixtures = [FIXTURES_DIR / "auth.json"]

    def setUp(self) -> None:
        self.user_a_username = "abc"
        self.user_b_password = "easy_password"
        user_a = User.objects.create(username=self.user_a_username)
        user_a.set_password(self.user_b_password)
        user_a.save()
        self.user_a = user_a
        self.client.login(username=self.user_a_username, password=self.user_b_password)

    def test_invalid_project_id(self):
        _choice = random.choice(utils.blocklist.data)
        project_id = _choice
        u = User.objects.first()
        with self.assertRaises(ValidationError):
            obj = Project(user=u, project_id=project_id)
            obj.full_clean()

    def test_invalid_slugified_project_id(self):
        _choice = random.choice(utils.blocklist.data)
        project_id = slugify(_choice)
        u = User.objects.first()
        with self.assertRaises(ValidationError):
            obj = Project(user=u, project_id=project_id)
            obj.full_clean()

    def test_project_delete(self):
        u = User.objects.first()
        obj = Project(user=u, project_id="test")
        obj.save()
        self.assertEqual(Project.objects.count(), 1)
        obj.delete()
        self.assertEqual(Project.objects.count(), 0)

    def test_project_create(self):
        u = User.objects.first()
        obj = Project(user=u, project_id="test")
        obj.save()
        self.assertEqual(Project.objects.count(), 1)

    def test_project_detail_view(self):
        obj = Project(user=self.user_a, project_id="test-123")
        obj.save()
        self.assertEqual(Project.objects.count(), 1)
        response = self.client.get(f"/projects/{obj.project_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/project_update.html")

    def test_project_delete_view(self):
        obj = Project(user=self.user_a, project_id="test-123df")
        obj.save()
        self.assertEqual(Project.objects.count(), 1)
        headers = {
            "HTTP_HX_Request": "true",
        }
        response = self.client.delete(f"/projects/{obj.project_id}/delete/", **headers)
        self.assertEqual(response.status_code, 200)
