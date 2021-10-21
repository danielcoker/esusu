from secrets import token_hex
from random import randint
import json

from django.urls import reverse

import pytest

from .. import factories as f


pytestmark = pytest.mark.django_db


def test_create_membership(client):
    group = f.GroupFactory()
    user = f.UserFactory()
    data = {'group': group.id}

    url = reverse('memberships-list')

    client.login(user)
    response = client.post(url, data)

    assert response.status_code == 201


def test_create_membership_by_token(client):
    group = f.GroupFactory()
    user = f.UserFactory()
    data = {'group_token': group.token}

    url = reverse('memberships-token')

    client.login(user)
    response = client.post(url, data)

    assert response.status_code == 201


def test_bulk_create_membership(client):
    group = f.GroupFactory()
    user1 = f.UserFactory()
    user2 = f.UserFactory()
    user3 = f.UserFactory()
    data = {
        'bulk_memberships': [
            {'email': user1.email},
            {'email': user2.email},
            {'email': user3.email},
        ],
        'group_id': group.id
    }

    url = reverse('memberships-bulk-create')

    client.login(group.owner)
    response = client.post(url, data=json.dumps(
        data), content_type='application/json')
    response_data = json.loads(response.content)['data']

    assert response.status_code == 201
    assert len(response_data) == 3


def test_list_memberships(client):
    group = f.GroupFactory()
    membership3 = f.MembershipFactory(group=group)
    membership2 = f.MembershipFactory(group=group)
    membership1 = f.MembershipFactory(group=group)

    url = f"{reverse('memberships-list')}?group={group.id}"

    client.login(group.owner)
    response = client.get(url)
    response_data = json.loads(response.content)['data']

    assert response.status_code == 200
    assert response_data[0]['id'] == membership1.id
    assert response_data[1]['id'] == membership2.id
    assert response_data[2]['id'] == membership3.id


def test_retrieve_membereship(client):
    membership = f.MembershipFactory()

    url = reverse('memberships-detail', kwargs={'pk': membership.id})

    client.login(membership.user)
    response = client.get(url)

    assert response.status_code == 200


def test_retrieve_non_existent_membership(client):
    user = f.UserFactory()

    url = reverse('memberships-detail', kwargs={'pk': randint(100, 200)})

    client.login(user)
    response = client.get(url)

    assert response.status_code == 404


def test_delete_membership(client):
    membership = f.MembershipFactory()

    url = reverse('memberships-detail', kwargs={'pk': membership.id})

    client.login(membership.user)
    response = client.delete(url)

    assert response.status_code == 204


def test_delete_non_existent_membership(client):
    user = f.UserFactory()

    url = reverse('memberships-detail', kwargs={'pk': randint(100, 200)})

    client.login(user)
    response = client.delete(url)

    assert response.status_code == 404
