from datetime import datetime

from django.test import TestCase

from fleet.tests.test_fleet import sample_airplane_type, sample_airplane
from flight_ops.models import Flight, Route, Crew
from location.tests.test_location import (
    sample_airport, sample_country, sample_city
)


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_route(**params):
    """
    Create a sample route with source and destination airports passed
    as a parameter.
    """

    defaults = {
        "distance": 1150,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    """Create a sample flight with route and airplane passed as a parameter."""

    defaults = {
        "number": "AB1234",
        "departure_time": datetime.strptime(
            "2024-09-01 10:15:00", "%Y-%m-%d %H:%M:%S"
        ),
        "arrival_time": datetime.strptime(
            "2024-09-01 14:30:00", "%Y-%m-%d %H:%M:%S"
        )
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


class CrewModelTests(TestCase):
    def test_crew_str(self):
        crew = sample_crew()
        expected_str = f"{crew.last_name}, {crew.first_name}"
        self.assertEqual(str(crew), expected_str)


class RouteModelTests(TestCase):
    def setUp(self):
        country = sample_country()
        city = sample_city(country=country)
        self.source = sample_airport(closest_big_city=city)
        self.destination = sample_airport(
            name="Gatwick", closest_big_city=city
        )
        self.route = sample_route(
            source=self.source, destination=self.destination
        )

    def test_route_str(self):
        expected_str = (f"from {self.source} to {self.destination} "
                        f"({self.route.distance} km)")
        self.assertEqual(str(self.route), expected_str)


class FlightModelTests(TestCase):
    def setUp(self):
        country = sample_country()
        city = sample_city(country=country)
        source = sample_airport(closest_big_city=city)
        destination = sample_airport(name="Gatwick", closest_big_city=city)
        route = sample_route(source=source, destination=destination)
        airplane_type = sample_airplane_type()
        airplane = sample_airplane(airplane_type=airplane_type)
        self.flight = sample_flight(route=route, airplane=airplane)

    def test_flight_str(self):
        expected_str = (f"Flight {self.flight.number} "
                        f"{self.flight.route.__str__()}")
        self.assertEqual(str(self.flight), expected_str)
