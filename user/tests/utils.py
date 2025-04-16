from django.contrib.auth import get_user_model


def sample_user(**params):
    defaults = {
        "email": "test_user@test.com",
        "password": "test1234",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)
