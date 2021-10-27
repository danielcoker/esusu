import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

from .models import PaymentList


def generate_payment_list(**kwargs):
    """
    Shuffle membership list and generate a payment list schedule for members.

    Kwargs Content:
    - memberships
    - group
    - cycle
    - start_date
    """
    random.shuffle(kwargs['memberships'])

    next_payment_date = datetime.strptime(kwargs['start_date'], '%Y-%m-%d') + \
        relativedelta(months=+1)

    # Save the value in the payment list tables.
    for idx, member in enumerate(kwargs['memberships']):
        PaymentList.objects.update_or_create(
            order=idx+1, group=kwargs['group'], cycle=kwargs['cycle'], payment_date=next_payment_date, user=member.user)
        next_payment_date = next_payment_date + relativedelta(months=+1)
