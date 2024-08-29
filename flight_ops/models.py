from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from fleet.models import Airplane
from location.models import Airport


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes"
    )
    distance = models.IntegerField()

    @staticmethod
    def validate_source_and_destination(source, destination, error_to_raise):
        if source.id == destination.id:
            raise error_to_raise(
                _("Source and destination airports must be different.")
            )

    def clean(self):
        Route.validate_source_and_destination(
            self.source,
            self.destination,
            ValidationError
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
        return super(Route, self).save(
            force_insert, force_update, using, update_fields, *args
        )

    def __str__(self):
        return f"from {self.source} to {self.destination} ({self.distance} km)"


class Flight(models.Model):
    number = models.CharField(max_length=60)
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["departure_time", "arrival_time"]

    def __str__(self):
        return f"Flight {self.number} {self.route.__str__()}"
