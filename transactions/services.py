import json

from esusu.settings import env

import requests


class Paystack():
    secret_key = None
    request = requests
    auth_header = {}

    def __init__(self, secret_key=None):
        self.secret_key = secret_key or env('PAYSTACK_SECRET_KEY')
        self.auth_header = {'Authorization': f'Bearer {self.secret_key}'}

    def verify_account_number(self, account_number, bank_code):
        """
        Verify account number is valid.
        https://paystack.com/docs/transfers/single-transfers#verify-the-account-number
        """
        params = {'account_number': account_number, 'bank_code': bank_code}
        response = self.request.get('https://api.paystack.co/bank/resolve',
                                    params=params,
                                    headers=self.auth_header)

        return json.loads(response.content)

    def create_transfer_recipient(self, **kwargs):
        """
        Create a transfer recipient.
        https://paystack.com/docs/transfers/single-transfers#create-a-transfer-recipient
        """
        response = self.request.post(
            'https://api.paystack.co/transferrecipient', data=kwargs, headers=self.auth_header)

        return json.loads(response.content)
