from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import NotFound

from base.utils import db
from users.models import User

from .models import Membership


def get_members_from_bulk(bulk_data, **additional_fields):
    """
    Convert a list of `bulk_data` into a list of members.

    :param bulk_data: List of members in bulk format.
    :param additional_fields: Additional fields when instantiating each task.

    :reeturn: List of `Member` instances.
    """
    members = []

    for data in bulk_data:
        data_copy = data.copy()
        email = data_copy.pop('email')

        try:
            user = User.objects.get(email=email)
            data_copy['user'] = user
        except User.DoesNotExist:
            raise NotFound(_(f'{email} does not exist.'))

        data_copy.update(**additional_fields)
        members.append(Membership(**data_copy))

    return members


def create_members_from_bulk(bulk_data, **additional_fields):
    """
    Create members from `bulk_data`

    :param bulk_data: List of dicts.
    :param additional_fields: Additional fields when instantiating each task.

    :return: List of created `Member` instances.
    """
    members = get_members_from_bulk(bulk_data, **additional_fields)
    # print(members)
    db.save_in_bulk(members)

    return members
