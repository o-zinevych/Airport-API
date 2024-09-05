from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from booking.models import Order, get_deleted_user
from booking.serializers import OrderListSerializer, OrderSerializer
from fleet.tests.test_fleet import sample_airplane_type, sample_airplane
from flight_ops.tests.test_flight_ops import sample_flight, sample_route
from location.tests.test_location import (
    sample_country, sample_city, sample_airport
)

ORDER_URL = reverse("booking:order-list")


def sample_user(**params):
    defaults = {
        "email": "test_user@test.com",
        "password": "test1234",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = sample_user()
        self.order = Order.objects.create(user=self.user)

    def test_order_str(self):
        self.assertEqual(str(self.order), f"order {self.order.id}")

    def test_deleted_user(self):
        deleted_user = get_deleted_user()
        self.assertEqual(deleted_user.email, "deleted_user@airport.com")

        self.user.delete()
        self.order.refresh_from_db()
        self.assertEqual(self.order.user, deleted_user)


class UnauthenticatedOrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

        country = sample_country()
        city = sample_city(country=country)
        source = sample_airport(closest_big_city=city)
        destination = sample_airport(name="Gatwick", closest_big_city=city)
        route = sample_route(source=source, destination=destination)
        airplane_type = sample_airplane_type()
        airplane = sample_airplane(airplane_type=airplane_type)
        self.flight = sample_flight(route=route, airplane=airplane)

    def test_orders_list_has_auth_user_orders(self):
        test_user_order = Order.objects.create(user=self.user)
        another_user = sample_user(email="another@test.com")
        another_user_order = Order.objects.create(user=another_user)

        test_user_serializer = OrderListSerializer(test_user_order)
        another_user_serializer = OrderListSerializer(another_user_order)

        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(test_user_serializer.data, response.data["results"])
        self.assertNotIn(
            another_user_serializer.data, response.data["results"]
        )

    def test_create_order_with_tickets_and_auth_user_by_default(self):
        payload = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
                {"row": 1, "seat": 2, "flight": self.flight.id}
            ]
        }
        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(pk=response.data["id"])
        serializer = OrderSerializer(order)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(order.user, self.user)

    def test_ticket_seat_and_row_validation(self):
        non_unique_payload = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
                {"row": 1, "seat": 1, "flight": self.flight.id}
            ]
        }
        with self.assertRaises(ValidationError):
            self.client.post(
                ORDER_URL, non_unique_payload, format="json"
            )

        non_existent_row_payload = {
            "tickets": [{"row": 40, "seat": 1, "flight": self.flight.id}]
        }
        response = self.client.post(
                ORDER_URL, non_existent_row_payload, format="json"
            )
        self.assertIn(
            "row number must be in the available range",
            str(response.data["tickets"][0]["row"])
        )

        non_existent_seat_payload = {
            "tickets": [{"row": 1, "seat": 10, "flight": self.flight.id}]
        }
        response = self.client.post(
                ORDER_URL, non_existent_seat_payload, format="json"
            )
        self.assertIn(
            "seat number must be in the available range",
            str(response.data["tickets"][0]["seat"])
        )
