import django
from .fixtures import *


def pytest_configure(config):
    django.setup()
