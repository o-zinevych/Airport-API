from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fleet.models import Airplane, AirplaneType
from fleet.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("fleet:airplane-type-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "Boeing 737-800",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    """Create a sample airplane with its type passed as a parameter."""

    defaults = {
        "name": "EI-EPC",
        "rows": 30,
        "seats_in_row": 6,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def airplane_type_detail_url(airplane_type_id):
    return reverse("fleet:airplane-type-detail", args=[airplane_type_id])


class AirplaneTypeModelTest(TestCase):
    def test_airplane_type_str(self):
        airplane_type = sample_airplane_type()
        self.assertEqual(str(airplane_type), airplane_type.name)


class AirplaneModelTest(TestCase):
    def setUp(self):
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane(airplane_type=self.airplane_type)

    def test_plane_capacity(self):
        capacity = self.airplane.rows * self.airplane.seats_in_row
        self.assertEqual(self.airplane.plane_capacity, capacity)

    def test_airplane_str(self):
        expected_str = f"{self.airplane.name}, type: {self.airplane_type.name}"
        self.assertEqual(str(self.airplane), expected_str)


class PublicAirplaneTypesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = sample_airplane_type()

    def test_airplane_type_list(self):
        sample_airplane_type(name="Airbus A320s")
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_type_retrieve(self):
        serializer = AirplaneTypeSerializer(self.airplane_type)
        response = self.client.get(
            airplane_type_detail_url(self.airplane_type.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        user = get_user_model().objects.create_user(
            email="test@test.com", password="test1234"
        )
        self.client.force_authenticate(user)

        payload = {
            "name": "Boeing 737-800",
        }
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin_user@airport.com",
            password="admin4321"
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_airplane_type(self):
        payload = {
            "name": "Boeing 737-800",
        }
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane_type = AirplaneType.objects.get(pk=response.data["id"])
        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(response.data, serializer.data)
