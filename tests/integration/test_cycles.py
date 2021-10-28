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
    cycle_id = json.loads(response.content)['data']['id']

    # Assert that cycle was set successfully.
    assert response.status_code == 200

    url = reverse('groups-detail', kwargs={'pk': group.id})
    response = client.get(url)
    response_data = json.loads(response.content)['data']

    # Assert that the current cycle on the group is updated.
    assert response_data['current_cycle'] == 1

    url = reverse('cycles-detail', kwargs={'pk': cycle_id})
    response = client.get(url)
    response_data = json.loads(response.content)['data']

    expected_end_date = data['start_date'] + \
        timedelta(days=21)

    # Assert that the end date is updated appropriately.
    assert response_data['end_date'] == expected_end_date.strftime('%Y-%m-%d')
