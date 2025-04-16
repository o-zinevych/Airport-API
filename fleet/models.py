from django.db import models


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        db_table = "fleet_airplane_type"

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.DO_NOTHING,
        related_name="airplanes"
    )

    class Meta:
        ordering = ["name"]

    @property
    def plane_capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name}, type: {self.airplane_type.name}"
