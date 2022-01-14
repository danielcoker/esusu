from datetime import timedelta

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

    db.save_in_bulk(members)

    return members


def get_cycle_end_date(start_date, member_count):
    """
    Get the end date of a cycle from its start date and the number of group members.

    :param start_date: The cycle start date.
    :param member_count: The number of members in the group.

    :return: The cycle end date.
    """
    return start_date + timedelta(days=member_count*7)
