import pytest


@pytest.fixture
def client():
    from rest_framework.test import APIClient

    class _Client(APIClient):
        def login(self, user) -> bool:
            if not user:
                return False

            token = user.generate_jwt_token()
            self.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            return True

    return _Client()
