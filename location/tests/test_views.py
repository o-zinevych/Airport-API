from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from location.models import Country, City
from location.serializers import CountrySerializer, CityListSerializer
from location.tests.utils import sample_country, sample_city
from user.tests.utils import sample_user

COUNTRY_URL = reverse("location:country-list")
CITY_URL = reverse("location:city-list")


def city_detail_url(city_id):
    return reverse("location:city-detail", args=[city_id])


class PublicCountryAPITests(TestCase):
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


class AdminCountryAPITests(TestCase):
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


class PublicCityAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = sample_country()
        self.city = sample_city(country=self.country)
        self.payload = {"name": "Cambridge", "country": self.country}

    def test_city_list(self):
        sample_city(name="Cambridge", country=self.country)
        cities = City.objects.all()
        serializer = CityListSerializer(cities, many=True)

        response = self.client.get(CITY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_city_detail(self):
        serializer = CityListSerializer(self.city)
        response = self.client.get(city_detail_url(self.city.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_city_forbidden_for_anon_users(self):
        response = self.client.post(CITY_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_city_forbidden_for_auth_users(self):
        self.client.force_authenticate(user=sample_user())
        response = self.client.post(CITY_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCityAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin4321"
        )
        self.client.force_authenticate(user=self.admin_user)

        country = sample_country()
        self.payload = {"name": "Cambridge", "country": country.id}

    def test_create_city(self):
        response = self.client.post(CITY_URL, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
