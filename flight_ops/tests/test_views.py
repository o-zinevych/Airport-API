from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from booking.tests.test_views import sample_user
from flight_ops.models import Crew
from flight_ops.serializers import CrewSerializer
from flight_ops.tests.utils import sample_crew

CREW_URL = reverse("flight-ops:crew-list")


def crew_detail_url(crew_id):
    return reverse("flight-ops:crew-detail", args=[crew_id])


class PublicCrewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_crew_forbidden_for_anon_users(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crew_forbidden_for_non_staff_users(self):
        user = sample_user()
        self.client.force_authenticate(user)

        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin4321"
        )
        self.client.force_authenticate(self.admin_user)
        self.crew = sample_crew()

    def test_crew_list(self):
        sample_crew()
        crew = Crew.objects.all()
        serializer = CrewSerializer(crew, many=True)

        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crew_detail(self):
        serializer = CrewSerializer(self.crew)
        response = self.client.get(crew_detail_url(self.crew.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_crew(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(CREW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        crew = Crew.objects.get(pk=response.data["id"])
        serializer = CrewSerializer(crew)
        self.assertEqual(response.data, serializer.data)
