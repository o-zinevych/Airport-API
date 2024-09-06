from django.test import TestCase

from booking.models import Order, get_deleted_user, Ticket
from flight_ops.tests.utils import sample_flight
from user.tests.utils import sample_user


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


class TicketModelTest(TestCase):
    def setUp(self):
        self.flight = sample_flight()

    def test_ticket_str(self):
        order = Order.objects.create(user=sample_user())
        ticket = Ticket.objects.create(
            row=1, seat=5, flight=self.flight, order=order
        )
        self.assertEqual(
            f"Ticket for row 1, seat 5, flight {self.flight.number}",
            str(ticket)
        )
