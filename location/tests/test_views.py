from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from location.models import Country
from location.serializers import CountrySerializer
from location.tests.utils import sample_country, sample_city
from user.tests.utils import sample_user

COUNTRY_URL = reverse("location:country-list")


class PublicCountryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = sample_country()

    def test_country_list(self):
        sample_country(name="US")
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)

        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_country_forbidden(self):
        user = sample_user()
        self.client.force_authenticate(user=user)
        payload = {"name": "US"}
        response = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin4321"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_country(self):
        payload = {"name": "US"}
        response = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
