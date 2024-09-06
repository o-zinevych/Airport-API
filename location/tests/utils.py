from location.models import Country, City, Airport


def sample_country(**params):
    defaults = {
        "name": "UK",
    }
    defaults.update(params)

    return Country.objects.create(**defaults)


def sample_city(**params):
    """Create a sample city with Country passed as a parameter."""

    defaults = {
        "name": "London",
    }
    defaults.update(params)

    return City.objects.create(**defaults)


def sample_airport(**params):
    """Create a sample airport with City passed as a parameter."""
    defaults = {
        "name": "Heathrow",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)
