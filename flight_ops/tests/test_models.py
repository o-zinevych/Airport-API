from django.test import TestCase

from flight_ops.tests.utils import sample_crew, sample_route, sample_flight


class CrewModelTests(TestCase):
    def test_crew_str(self):
        crew = sample_crew()
        expected_str = f"{crew.last_name}, {crew.first_name}"
        self.assertEqual(str(crew), expected_str)


class RouteModelTests(TestCase):
    def setUp(self):
        self.route = sample_route()

    def test_route_str(self):
        expected_str = (f"from {self.route.source} to {self.route.destination}"
                        f" ({self.route.distance} km)")
        self.assertEqual(str(self.route), expected_str)


class FlightModelTests(TestCase):
    def setUp(self):
        self.flight = sample_flight()

    def test_flight_str(self):
        expected_str = (f"Flight {self.flight.number} "
                        f"{self.flight.route.__str__()}")
        self.assertEqual(str(self.flight), expected_str)
