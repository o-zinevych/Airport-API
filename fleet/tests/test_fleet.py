from django.test import TestCase

from fleet.models import Airplane, AirplaneType


def sample_airplane_type(**params):
    defaults = {
        "name": "Boeing 737-800",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    """Create a sample airplane with its type passed as a parameter."""

    defaults = {
        "name": "EI-EPC",
        "rows": 30,
        "seats_in_row": 6,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


class AirplaneTypeModelTest(TestCase):
    def test_airplane_type_str(self):
        airplane_type = sample_airplane_type()
        self.assertEqual(str(airplane_type), airplane_type.name)


class AirplaneModelTest(TestCase):
    def setUp(self):
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane(airplane_type=self.airplane_type)

    def test_plane_capacity(self):
        capacity = self.airplane.rows * self.airplane.seats_in_row
        self.assertEqual(self.airplane.plane_capacity, capacity)

    def test_airplane_str(self):
        expected_str = f"{self.airplane.name}, type: {self.airplane_type.name}"
        self.assertEqual(str(self.airplane), expected_str)
