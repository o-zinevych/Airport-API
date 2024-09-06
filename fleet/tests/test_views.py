from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from fleet.models import Airplane, AirplaneType
from fleet.serializers import (
    AirplaneTypeSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneSerializer,
)
from fleet.tests.utils import sample_airplane_type, sample_airplane
from user.tests.utils import sample_user

AIRPLANE_TYPE_URL = reverse("fleet:airplane-type-list")
AIRPLANE_URL = reverse("fleet:airplane-list")


def airplane_type_detail_url(airplane_type_id):
    return reverse("fleet:airplane-type-detail", args=[airplane_type_id])


def airplane_detail_url(airplane_id):
    return reverse("fleet:airplane-detail", args=[airplane_id])


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


class PublicAirplaneAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane(airplane_type=self.airplane_type)

    def test_airplane_list(self):
        sample_airplane(name="AB-CDE", airplane_type=self.airplane_type)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airplane_detail(self):
        serializer = AirplaneDetailSerializer(self.airplane)
        response = self.client.get(airplane_detail_url(self.airplane.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airplane_forbidden(self):
        user = sample_user()
        self.client.force_authenticate(user)

        payload = {
            "name": "EI-EPC",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin_user@airport.com",
            password="admin4321"
        )
        self.client.force_authenticate(self.admin_user)

        self.airplane_type = sample_airplane_type()

    def test_create_airplane_type(self):
        payload = {
            "name": "EI-EPC",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(pk=response.data["id"])
        serializer = AirplaneSerializer(airplane)
        self.assertEqual(response.data, serializer.data)
