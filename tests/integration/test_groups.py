from secrets import token_hex
from random import randint
import json

from django.urls import reverse

import pytest

from .. import factories as f


pytestmark = pytest.mark.django_db


def test_retrieve_group_by_id(client):
    group = f.GroupFactory()
    url = reverse('groups-detail', kwargs={'pk': group.id})

    response = client.get(url)

    assert response.status_code == 200


def test_retrieve_by_non_existent_group_id(client):
    url = reverse('groups-detail', kwargs={'pk': randint(1, 100)})

    response = client.get(url)

    assert response.status_code == 404


def test_create_group(client):
    user = f.UserFactory()
    url = reverse('groups-list')
    data = {
        'name': 'group name',
        'description': 'group description',
        'max_capacity': 5,
        'amount_to_save': 1000,
        'is_searchable': True
    }

    client.login(user)
    response = client.post(url, data)

    assert response.status_code == 201


def test_list_groups(client):
    group3 = f.GroupFactory(token=token_hex(10).upper())
    group2 = f.GroupFactory(token=token_hex(10).upper())
    group1 = f.GroupFactory(token=token_hex(10).upper())

    url = reverse('groups-list')

    response = client.get(url)
    response_data = json.loads(response.content)['data']

    assert response.status_code == 200
    assert response_data[0]['id'] == group1.id
    assert response_data[1]['id'] == group2.id
    assert response_data[2]['id'] == group3.id


def test_list_only_searchable_groups(client):
    group3 = f.GroupFactory(token=token_hex(10).upper())
    group2 = f.GroupFactory(token=token_hex(10).upper(), is_searchable=False)
    group1 = f.GroupFactory(token=token_hex(10).upper())

    url = reverse('groups-list')

    response = client.get(url)
    response_data = json.loads(response.content)['data']

    assert response.status_code == 200
    assert len(response_data) == 2
    assert response_data[0]['id'] == group1.id
    assert response_data[1]['id'] == group3.id


def test_update_group(client):
    group = f.GroupFactory()

    url = reverse('groups-detail', kwargs={'pk': group.id})
    data = {
        'name': 'updated name',
        'description': 'updated description',
        'max_capacity': 5,
        'amount_to_save': 1000,
        'is_searchable': True
    }

    response = client.put(url, data)
    assert response.status_code == 403

    client.login(group.owner)
    response = client.put(url, data)
    response.status_code == 200
    response_data = json.loads(response.content)['data']

    assert response_data['name'] == data['name']
    assert response_data['description'] == data['description']


def test_update_a_different_owner_group(client):
    user = f.UserFactory()
    group = f.GroupFactory()

    url = reverse('groups-detail', kwargs={'pk': group.id})
    data = {
        'name': 'updated name',
        'description': 'updated description',
        'max_capacity': 5,
        'amount_to_save': 1000,
        'is_searchable': True
    }

    client.login(user)
    response = client.put(url, data)

    assert response.status_code == 403


def test_update_non_existent_group(client):
    user = f.UserFactory()

    url = reverse('groups-detail', kwargs={'pk': randint(1, 100)})
    data = {
        'name': 'updated name',
        'description': 'updated description',
        'max_capacity': 5,
        'amount_to_save': 1000,
        'is_searchable': True
    }

    client.login(user)
    response = client.put(url, data)

    assert response.status_code == 404


def test_delete_group(client):
    group = f.GroupFactory()

    url = reverse('groups-detail', kwargs={'pk': group.id})

    client.login(group.owner)
    response = client.delete(url)

    assert response.status_code == 204


def test_delete_a_different_owner_group(client):
    user = f.UserFactory()
    group = f.GroupFactory()

    url = reverse('groups-detail', kwargs={'pk': group.id})

    client.login(user)
    response = client.delete(url)

    assert response.status_code == 403


def test_delete_non_existent_group(client):
    group = f.GroupFactory()

    url = reverse('groups-detail', kwargs={'pk': randint(1, 100)})

    client.login(group.owner)
    response = client.delete(url)

    assert response.status_code == 404
