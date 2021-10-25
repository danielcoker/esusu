from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated


from base.permissions import IsOwner
from base.mixins import SuccessMessageMixin

from .models import Bank, Card
from .services import Paystack
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
