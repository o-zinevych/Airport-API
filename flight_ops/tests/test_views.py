from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from booking.tests.test_views import sample_user
from flight_ops.models import Crew, Route, Flight
from flight_ops.serializers import (
    CrewSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    RouteSerializer,
    FlightListSerializer,
)
from flight_ops.tests.utils import sample_crew, sample_route, sample_flight
from location.tests.utils import sample_country, sample_city, sample_airport

CREW_URL = reverse("flight-ops:crew-list")
ROUTE_URL = reverse("flight-ops:route-list")
FLIGHT_URL = reverse("flight-ops:flight-list")


def crew_detail_url(crew_id):
    return reverse("flight-ops:crew-detail", args=[crew_id])


def route_detail_url(route_id):
    return reverse("flight-ops:route-detail", args=[route_id])


def flight_detail_url(flight_id):
    return reverse("flight-ops:flight-detail", args=[flight_id])


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


class PublicRouteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.route = sample_route()

    def test_route_list(self):
        Route.objects.create(
            source=self.route.source,
            destination=self.route.destination,
            distance=1000,
        )
        routes = Route.objects.select_related("source", "destination")
        serializer = RouteListSerializer(routes, many=True)

        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_route_detail(self):
        serializer = RouteDetailSerializer(self.route)
        response = self.client.get(route_detail_url(self.route.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_route_forbidden_for_anon_users(self):
        payload = {
            "source_id": self.route.source_id,
            "destination_id": self.route.destination_id,
            "distance": 2000,
        }
        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_route_forbidden_for_auth_users(self):
        user = sample_user()
        self.client.force_authenticate(user)
        payload = {
            "source_id": self.route.source_id,
            "destination_id": self.route.destination_id,
            "distance": 2000,
        }

        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin4321"
        )
        self.client.force_authenticate(self.admin_user)
        self.route = sample_route()

    def test_create_route(self):
        payload = {
            "source": self.route.source_id,
            "destination": self.route.destination_id,
            "distance": 2000
        }
        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        route = Route.objects.get(pk=response.data["id"])
        serializer = RouteSerializer(route)
        self.assertEqual(response.data, serializer.data)

    def test_route_source_and_destination_validation_when_creating(self):
        payload = {
            "source": self.route.source_id,
            "destination": self.route.source_id,
            "distance": 2000
        }

        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PublicFlightAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.flight = sample_flight()

        self.payload = {
            "number": self.flight.number,
            "route": self.flight.route_id,
            "airplane": self.flight.airplane_id,
            "departure_time": self.flight.departure_time,
            "arrival_time": self.flight.arrival_time,
        }

    def test_flight_list_with_seats_available(self):
        Flight.objects.create(
            number="CD4321",
            route=self.flight.route,
            airplane=self.flight.airplane,
            departure_time=self.flight.departure_time,
            arrival_time=self.flight.arrival_time
        )
        flights = Flight.objects.annotate(
                seats_available=F("airplane__seats_in_row")
                * F("airplane__rows") - Count("tickets")
            )
        serializer = FlightListSerializer(flights, many=True)

        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flight_list_source_and_destination_filter(self):
        country = sample_country(name="USA")
        los_angeles = sample_city(name="Los Angeles", country=country)
        nyc = sample_city(name="New York City", country=country)
        filter_source = sample_airport(name="JFK", closest_big_city=nyc)
        filter_destination = sample_airport(
            name="LAX", closest_big_city=los_angeles
        )
        filter_route = Route.objects.create(
            source=filter_source,
            destination=filter_destination,
            distance=1000,
        )
        filter_flight = Flight.objects.create(
            number="CD4321",
            route=filter_route,
            airplane=self.flight.airplane,
            departure_time=self.flight.departure_time,
            arrival_time=self.flight.arrival_time,
        )

        response = self.client.get(FLIGHT_URL, {"source": filter_source.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], filter_flight.pk)

        response = self.client.get(
            FLIGHT_URL, {"destination": filter_destination.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], filter_flight.pk)

    def test_flight_list_departure_date_filter(self):
        departure_date = "2024-12-06"
        departure_time = datetime.strptime(
            f"{departure_date} 11:15:00", "%Y-%m-%d %H:%M:%S"
        )
        filter_flight = Flight.objects.create(
            number="CD4321",
            route=self.flight.route,
            airplane=self.flight.airplane,
            departure_time=departure_time,
            arrival_time=self.flight.arrival_time,
        )

        response = self.client.get(
            FLIGHT_URL, {"departure_date": departure_date}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], filter_flight.pk)

    def test_flight_list_arrival_date_filter(self):
        arrival_date = "2024-12-07"
        arrival_time = datetime.strptime(
            f"{arrival_date} 15:15:00", "%Y-%m-%d %H:%M:%S"
        )
        filter_flight = Flight.objects.create(
            number="CD4321",
            route=self.flight.route,
            airplane=self.flight.airplane,
            departure_time=arrival_time,
            arrival_time=self.flight.arrival_time,
        )

        response = self.client.get(
            FLIGHT_URL, {"departure_date": arrival_date}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], filter_flight.pk)

    def test_flight_detail_without_crew(self):
        response = self.client.get(flight_detail_url(self.flight.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("crew", response.data)

    def test_create_and_update_flight_forbidden_for_anon_users(self):
        create_response = self.client.post(FLIGHT_URL, self.payload)
        self.assertEqual(
            create_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        put_response = self.client.put(
            FLIGHT_URL, self.payload, **{"id": self.flight.id}
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_create_and_update_flight_forbidden_for_auth_users(self):
        user = sample_user()
        self.client.force_authenticate(user)

        create_response = self.client.post(FLIGHT_URL, self.payload)
        self.assertEqual(
            create_response.status_code, status.HTTP_403_FORBIDDEN
        )

        put_response = self.client.put(
            FLIGHT_URL, self.payload, **{"id": self.flight.id}
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_403_FORBIDDEN
        )
