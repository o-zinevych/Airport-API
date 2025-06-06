import uuid
from pathlib import Path

from django.db import models
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country,
        related_name="cities",
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "cities"

    def __str__(self):
        return f"{self.name} ({self.country.name})"


def airport_image_file_path(instance, filename):
    name = f"{slugify(instance.name)}-{uuid.uuid4()}" + Path(filename).suffix
    return Path("upload/airports/") / Path(name)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(
        City,
        related_name="airports",
        on_delete=models.CASCADE
    )
    image = models.ImageField(null=True, upload_to=airport_image_file_path)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.closest_big_city.__str__()}"
