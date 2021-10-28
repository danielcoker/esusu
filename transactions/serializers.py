from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied


from users.serializers import UserSerializer
from groups.serializers import GroupSerializer, CycleSerializer

from .models import Bank, Card, PaymentList, SavingsList, Transaction
from .utils import Paystack


class BankSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Bank
        fields = ('id', 'account_name', 'account_number', 'bank_code',
                  'bank_name', 'transfer_recipient', 'is_default', 'user', 'created_at')
        read_only_fields = ('account_name', 'bank_name', 'transfer_recipient',)

    def validate(self, attrs):
        paystack = Paystack()

        # Verify account number.
        response = paystack.verify_account_number(
            attrs['account_number'], attrs['bank_code'])

        if not response['status'] and 'bank code' in response['message']:
            raise serializers.ValidationError(
                {'bank_code': _(response['message'])})

        if not response['status'] and 'account name' in response['message']:
            raise serializers.ValidationError(
                {'account_number': _(response['message'])})

        if not response['status']:
            raise ValidationError(_(response['message']))

        # Check if this bank details already exist.
        bank_count = Bank.objects.filter(
            account_number=attrs['account_number'], bank_code=attrs['bank_code']).count()

        if bank_count > 0:
            raise PermissionDenied(
                _('This account number and bank already exist.'))

        # Create transfer recipient.
        response = paystack.create_transfer_recipient(type='nuban',
                                                      name=response['data']['account_name'],
                                                      account_number=attrs['account_number'],
                                                      bank_code=attrs['bank_code'],
                                                      currency='NGN')

        response_data = response['data']

        attrs['account_name'] = response_data['details']['account_name']
        attrs['transfer_recipient'] = response_data['recipient_code']
        attrs['bank_name'] = response_data['details']['bank_name']

        return attrs


class CardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Card
        fields = '__all__'

    def create(self, validated_data):
        signature = validated_data['signature']
        exp_month = validated_data['exp_month']
        exp_year = validated_data['exp_year']
        last4 = validated_data['last4']
        user = validated_data['user']

        card, created = Card.objects.update_or_create(
            signature=signature, exp_month=exp_month, exp_year=exp_year, last4=last4, user=user, defaults=validated_data)

        return card


class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=255, required=True)


class WebhookDataSerializer(serializers.Serializer):
    amount = serializers.CharField(max_length=255, required=True)
    reference = serializers.CharField(max_length=255, required=True)
    status = serializers.CharField(max_length=255, required=True)


class WebhookSerializer(serializers.Serializer):
    event = serializers.CharField(max_length=255, required=True)
    data = WebhookDataSerializer(source='*')


class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Transaction
        fields = ('id', 'reference', 'amount',
                  'type', 'status', 'comments', 'user',)


class SavingsListSerializer(serializers.ModelSerializer):
    cycle = CycleSerializer()
    transaction = TransactionSerializer()
    user = UserSerializer()

    class Meta:
        model = SavingsList
        fields = ('id', 'cycle', 'group', 'transaction', 'user',)


class PaymentListSerializer(serializers.ModelSerializer):
    cycle = CycleSerializer()
    transaction = TransactionSerializer()
    user = UserSerializer()

    class Meta:
        model = PaymentList
        fields = ('id', 'order', 'cycle', 'group',
                  'payment_date', 'transaction', 'user')
