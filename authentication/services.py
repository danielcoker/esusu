from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


def login(email: str, password: str):
    """
    Authenticate a user.
    """
    user = authenticate(username=email, password=password)

    if user is None:
        raise AuthenticationFailed(
            'Incorrect email or password.',
        )

    user.token = user.generate_jwt_token()

    return user
