from decimal import Decimal
from datetime import datetime, timedelta

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated


from base.permissions import IsOwner
from base.mixins import SuccessMessageMixin
from groups.models import Cycle, Group, Membership

from .models import Bank, Card, SavingsList, Transaction
from .utils import Paystack
from .serializers import BankSerializer, CardSerializer, VerifyPaymentSerializer


class BankViewset(SuccessMessageMixin, ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == 'list':
            qs = qs.filter(user=self.request.user)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CardViewSet(SuccessMessageMixin, ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = (IsAuthenticated, IsOwner,)
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == 'list':
            qs = qs.filter(user=self.request.user)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reference = serializer.data['reference']

        paystack = Paystack()
        response = paystack.verify_transaction(reference)
        response_data = response['data']

        if response_data['status'] != 'success':
            raise ValidationError(_('Unable to save card.'))

        serializer = self.get_serializer(
            data={**response_data['authorization'], 'reference': reference})
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionViewset(SuccessMessageMixin, ViewSet):
    permission_classes = (IsAuthenticated,)

    @action(methods=['GET'], detail=False)
    def save(self, request, **kwargs):
        # Fetch all the cycles that has their next saving date as today.
        cycles = Cycle.objects.select_related('group').filter(
            next_saving_date=datetime.now().date())

        for cycle in cycles:
            memberships = Membership.objects.filter(group=cycle.group)

            for membership in memberships:
                card = Card.objects.select_related(
                    'user').filter(user=membership.user).first()

                # Convert amount to save to the integer value.
                amount_to_save = int(
                    Decimal(cycle.group.amount_to_save.amount)) * 10
                print(amount_to_save)
                # Charge card
                paystack = Paystack()
                response = paystack.charge_authorization(
                    card.authorization_code, card.user.email, amount_to_save)

                response_data = response['data']

                amount = response_data['amount'] / 100
                reference = response_data['reference']
                type = 'savings'
                transaction_status = response_data['status']

                # Save to transaction.
                transaction = Transaction.objects.create(
                    amount=amount, reference=reference, type=type, status=transaction_status, user=card.user)

                # Save the transaction in savings list.
                SavingsList.objects.create(
                    cycle=cycle, group=cycle.group, transaction=transaction, user=card.user)

        # Update next saving date.
        if len(cycles) > 0 and cycles[0].end_date == datetime.now().date():
            next_saving_date = None
        else:
            next_saving_date = datetime.now().date() + \
                timedelta(days=7)

        cycles.update(next_saving_date=next_saving_date)

        self.success_message = 'Savings operation completed successfully.'

        return Response(status=status.HTTP_200_OK)
