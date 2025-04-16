from datetime import datetime

from flight_ops.models import Flight, Route, Crew


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
            "2024-09-01 10:15:00", "%Y-%m-%d %H-%M-%S"
        ),
        "arrival_time": datetime.strptime(
            "2024-09-01 14:30:00", "%Y-%m-%d %H-%M-%S"
        )
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)
