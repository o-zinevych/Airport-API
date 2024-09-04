from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from booking.models import Ticket, Order, get_deleted_user

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
