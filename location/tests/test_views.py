import os.path
from tempfile import NamedTemporaryFile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from location.models import Country, City, Airport
from location.serializers import (
    CountrySerializer,
    CityListSerializer,
    AirportListSerializer,
)
from location.tests.utils import sample_country, sample_city, sample_airport
from user.tests.utils import sample_user

COUNTRY_URL = reverse("location:country-list")
CITY_URL = reverse("location:city-list")
AIRPORT_URL = reverse("location:airport-list")


def city_detail_url(city_id):
    return reverse("location:city-detail", args=[city_id])

def airport_detail_url(airport_id):
    return reverse("location:airport-detail", args=[airport_id])

def airport_image_upload_url(airport_id):
    return reverse("location:airport-upload-image", args=[airport_id])


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


class PublicAirportAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.country = sample_country()
        self.city = sample_city(country=self.country)
        self.airport = sample_airport(closest_big_city=self.city)

        self.payload = {"name": "Gatwick", "closest_big_city": self.city}

    def test_airport_list(self):
        sample_airport(**self.payload)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airport_detail(self):
        serializer = AirportListSerializer(self.airport)
        response = self.client.get(airport_detail_url(self.airport.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airport_forbidden_for_anon_users(self):
        response = self.client.post(AIRPORT_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_airport_forbidden_for_auth_users(self):
        self.client.force_authenticate(user=sample_user())
        response = self.client.post(AIRPORT_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin4321"
        )
        self.client.force_authenticate(user=self.admin_user)

        country = sample_country()
        city = sample_city(country=country)
        self.payload = {"name": "Gatwick", "closest_big_city": city.id}

    def test_create_airport(self):
        response = self.client.post(AIRPORT_URL, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirportImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin4321"
        )
        self.client.force_authenticate(user=self.admin_user)
        self.country = sample_country()
        self.city = sample_city(country=self.country)
        self.airport = sample_airport(closest_big_city=self.city)

    def tearDown(self):
        self.airport.image.delete()

    def test_upload_image_to_airport(self):
        url = airport_image_upload_url(self.airport.id)
        with NamedTemporaryFile(suffix=".jpg") as temp_jpg:
            image = Image.new("RGB", (10, 10))
            image.save(temp_jpg, format="JPEG")
            temp_jpg.seek(0)
            response = self.client.post(
                url, {"image": temp_jpg}, format="multipart"
            )
        self.airport.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.airport.image.path))

    def test_upload_non_image_bad_request(self):
        response = self.client.post(
            airport_image_upload_url(self.airport.id),
            {"image": "not image"},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_to_airport_list(self):
        """Test that an airport is created but no image is uploaded"""
        with NamedTemporaryFile(suffix=".jpg") as temp_jpg:
            image = Image.new("RGB", (10, 10))
            image.save(temp_jpg, format="JPEG")
            temp_jpg.seek(0)
            response = self.client.post(
                AIRPORT_URL,
                {
                    "name": "Name",
                    "closest_big_city": self.city.id,
                    "image": temp_jpg,
                }
                , format="multipart"
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(name="Name")
        self.assertFalse(airport.image)
