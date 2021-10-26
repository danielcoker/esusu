from random import randint
import json

from django.urls import reverse

import pytest

from .. import factories as f


pytestmark = pytest.mark.django_db


def test_retrieve_bank_by_id(client):
    bank = f.BankFactory()
    url = reverse('banks-detail', kwargs={'pk': bank.id})

    client.login(bank.user)
    response = client.get(url)

    assert response.status_code == 200


def test_retrieve_by_non_existent_bank_id(client):
    user = f.UserFactory()
    url = reverse('banks-detail', kwargs={'pk': randint(1, 100)})

    client.login(user)
    response = client.get(url)

    assert response.status_code == 404


def test_create_bank(client):
    user = f.UserFactory()
    url = reverse('banks-list')
    data = {
        'account_number': '0242936133',
        'bank_code': '058'
    }

    client.login(user)
    response = client.post(url, data)

    assert response.status_code == 201


def test_list_banks(client):
    user = f.UserFactory()
    bank2 = f.BankFactory(user=user)
    bank1 = f.BankFactory(user=user)
    url = reverse('banks-list')

    client.login(user)
    response = client.get(url)
    response_data = json.loads(response.content)['data']

    assert response_data[0]['id'] == bank1.id
    assert response_data[1]['id'] == bank2.id


def test_delete_bank(client):
    bank = f.BankFactory()
    url = reverse('banks-detail', kwargs={'pk': bank.id})

    client.login(bank.user)
    response = client.delete(url)

    assert response.status_code == 204

    response = client.get(url)

    assert response.status_code == 404


def test_delete_non_existent_bank_id(client):
    bank = f.BankFactory()
    url = reverse('banks-detail', kwargs={'pk': randint(1, 100)})

    client.login(bank.user)
    response = client.delete(url)

    assert response.status_code == 404
