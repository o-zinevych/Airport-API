from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from flight_ops.models import Flight


def get_deleted_user():
    return get_user_model().objects.get_or_create(
        email="deleted_user@airport.com"
    )[0]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_deleted_user),
        related_name="orders",
    )

    def __str__(self):
        return f"order {self.id}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="The seat in this row is already taken for the flight. "
                "Choose a free one.",
            )
        ]

    def __str__(self):
        return (
            f"Ticket for row {self.row}, seat {self.seat}, "
            f"flight {self.flight.number}"
        )
