from django.test import TestCase

from fleet.tests.utils import sample_airplane_type, sample_airplane


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
