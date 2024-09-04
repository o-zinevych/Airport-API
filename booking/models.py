from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from rest_framework.exceptions import ValidationError

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

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        print(str(airplane))
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row")
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            print(count_attrs)
            if not 1 <= ticket_attr_value <= count_attrs:
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number must be "
                                          f"in the available range: "
                                          f"1 to {count_attrs}"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row, self.seat, self.flight.airplane, ValidationError
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super().save(
            force_insert, force_update, using, update_fields, *args
        )

    def __str__(self):
        return (
            f"Ticket for row {self.row}, seat {self.seat}, "
            f"flight {self.flight.number}"
        )
