import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_email_registration(self):
        with pytest.raises(ValueError) as exc_info:
            get_user_model().objects.create_user(email="", password="test1234")
        self.assertEqual(str(exc_info.value), "The given email must be set")
