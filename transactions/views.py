from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from base.permissions import IsOwner
from base.mixins import SuccessMessageMixin

from .models import Bank
from .serializers import BankSerializer


class BankViewset(SuccessMessageMixin, ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
