import random

from cfehome import utils
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.text import slugify

from .models import Project

User = get_user_model()

class ProjectTestCase(TestCase):
    fixtures = [settings.FIXTURES_DIR / "auth.json"]

    def test_invalid_project_id(self):
        _choice = random.choice(utils.blocklist.data)
        project_id = _choice
        u = User.objects.first()
        with self.assertRaises(ValidationError):
            obj = Project(user=u, project_id=project_id)
            obj.full_clean()

    def test_invalid_slufified_project_id(self):
        _choice = random.choice(utils.blocklist.data)
        project_id = slugify(_choice)
        u = User.objects.first()
        with self.assertRaises(ValidationError):
            obj =Project(user=u, project_id=project_id)
            obj.full_clean()
