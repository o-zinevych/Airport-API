from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.tests.utils import sample_user

USER_REGISTER_URL = reverse("user:create")
USER_ACCOUNT_URL = reverse("user:manage")


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_create_with_encrypted_password(self):
        payload = {"email": "test_user@test.com", "password": "test1234"}
        response = self.client.post(USER_REGISTER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertNotEqual(user.password, payload["password"])

    def test_user_detail_should_return_current_user(self):
        user = sample_user()
        self.client.force_authenticate(user)

        response = self.client.get(USER_ACCOUNT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.email, response.data["email"])

    def test_user_update_with_encrypted_password(self):
        user = sample_user()
        self.client.force_authenticate(user)
        payload = {"password": "1234test"}

        response = self.client.patch(USER_ACCOUNT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertNotEqual(user.password, payload["password"])

    def test_user_detail_is_staff_field_presence(self):
        user = sample_user()
        self.client.force_authenticate(user)
        response = self.client.get(USER_ACCOUNT_URL)
        self.assertNotIn("is_staff", response.data)

        superuser = get_user_model().objects.create_superuser(
            email="superuser@test.com", password="super1234")
        self.client.force_authenticate(superuser)
        response = self.client.get(USER_ACCOUNT_URL)
        self.assertIn("is_staff", response.data)
