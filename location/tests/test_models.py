from pathlib import Path

from django.test import TestCase
from django.utils.text import slugify

from location.models import airport_image_file_path
from location.tests.utils import sample_country, sample_city, sample_airport


class CountryModelTest(TestCase):
    def test_country_str(self):
        country = sample_country()
        self.assertEqual(str(country), country.name)


class CityModelTest(TestCase):
    def setUp(self):
        self.country = sample_country()
        self.city = sample_city(country=self.country)

    def test_city_str(self):
        expected_str = f"{self.city.name} ({self.country.name})"
        self.assertEqual(str(self.city), expected_str)


class AirportModelTest(TestCase):
    def setUp(self):
        self.city = sample_city(country=sample_country())
        self.airport = sample_airport(closest_big_city=self.city)

    def test_airport_str(self):
        expected_str = (f"{self.airport.name} - "
                        f"{str(self.airport.closest_big_city)}")
        self.assertEqual(str(self.airport), expected_str)

    def test_image_upload_path(self):
        start_of_path = Path("upload/airports/") / Path(
            f"{slugify(self.airport.name)}-"
        )
        test_path = airport_image_file_path(
            self.airport, f"{self.airport.name}.jpeg"
        )
        self.assertIn(str(start_of_path), str(test_path))
