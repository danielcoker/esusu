from datetime import datetime, timedelta
import json

from django.urls import reverse

import pytest

from .. import factories as f

pytestmark = pytest.mark.django_db


def test_set_cycle_start_date(client):
    user = f.UserFactory()
    group = f.GroupFactory(owner=user)
    f.MembershipFactory(group=group, user=user)
    f.MembershipFactory(group=group)
    f.MembershipFactory(group=group)
    url = reverse('cycles-set')
    data = {
        'start_date': datetime.now().date(),
        'group': group.id
    }

    assert group.current_cycle == None

    client.login(user)
    response = client.post(url, data)

    assert response.status_code == 200

    url = reverse('groups-detail', kwargs={'pk': group.id})
    response = client.get(url)
    response_data = json.loads(response.content)['data']

    assert response_data['current_cycle'] == 1

    # @TODO Hit get cycle endpoint to check end date is the correct date. (Correct Date: start_date + 3 weeks)
