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
