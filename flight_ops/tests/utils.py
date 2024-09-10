from datetime import datetime

from django.db import IntegrityError

from fleet.tests.utils import sample_airplane_type, sample_airplane
from flight_ops.models import Crew, Route, Flight
from location.tests.utils import sample_country, sample_city, sample_airport


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_route(**params):
    """
    Create a sample route with source and destination airports samples.
    """
    try:
        country = sample_country()
        city = sample_city(country=country)
        source = sample_airport(closest_big_city=city)
        destination = sample_airport(name="Gatwick", closest_big_city=city)
        defaults = {
            "source": source,
            "destination": destination,
            "distance": 1150,
        }
    except IntegrityError:
        defaults = {}
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    """Create a sample flight with route and airplane samples."""

    route = sample_route()
    airplane_type = sample_airplane_type()
    airplane = sample_airplane(airplane_type=airplane_type)
    defaults = {
        "number": "AB1234",
        "route": route,
        "airplane": airplane,
        "departure_time": datetime.strptime(
            "2024-09-01 10:15:00", "%Y-%m-%d %H:%M:%S"
        ),
        "arrival_time": datetime.strptime(
            "2024-09-01 14:30:00", "%Y-%m-%d %H:%M:%S"
        )
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)
