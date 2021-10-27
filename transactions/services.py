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
        PaymentList.objects.create(
            order=idx+1, group=kwargs['group'], cycle=kwargs['cycle'], payment_date=next_payment_date, user=member.user)
        next_payment_date = next_payment_date + relativedelta(months=+1)

    return True


def append_member_to_payment_list(**kwargs):
    """
    Append a member to the end of a payment list.

    Kwargs Content:
    - user
    - group
    - cycle
    """
    payment_list = PaymentList.objects.filter(
        cycle=kwargs['cycle'], group=kwargs['group']).order_by('-order').first()

    payment_date = payment_list.payment_date + relativedelta(months=+1)

    PaymentList.objects.create(
        order=payment_list.order+1, group=kwargs['group'], cycle=kwargs['cycle'], payment_date=payment_date, user=kwargs['user'])

    return True
