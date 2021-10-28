import secrets
from datetime import datetime

from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from django_pglocks import advisory_lock

from base.mixins import SuccessMessageMixin
from base.permissions import IsOwnerOrReadOnly
from transactions.models import PaymentList, SavingsList
from transactions.serializers import PaymentListSerializer, SavingsListSerializer
from transactions.services import generate_payment_list, append_member_to_payment_list

from .models import Cycle, Group, Membership
from .serializers import GroupSerializer, MembershipSerializer, MembershipBulkSerializer, CycleSerializer
from . import services


class GroupViewSet(SuccessMessageMixin, ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user,
                        token=secrets.token_hex(10).upper())

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('owner')

        if self.action == 'list':
            qs = qs.filter(is_searchable=True)

        return qs

    def retrieve(self, request, *args, **kwargs):
        if self.action == 'token':
            self.lookup_field = 'token'

        self.object = get_object_or_404(self.get_queryset(), **kwargs)

        serializer = self.get_serializer(self.object)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='token/(?P<token>[^/.]+)')
    def token(self, request, token, pk=None):
        return self.retrieve(request, token=token)

    @action(methods=['GET'], detail=True)
    def savings(self, request, pk=None):
        savings = SavingsList.objects.filter(group=pk)

        cycle_number = request.query_params.get('cycle')
        if cycle_number:
            cycle = Cycle.objects.filter(cycle_number=cycle_number).first()
            savings = savings.filter(cycle=cycle)

        serializer = SavingsListSerializer(savings, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def payments(self, request, pk=None):
        payments = PaymentList.objects.filter(group=pk)

        cycle_number = request.query_params.get('cycle')
        if cycle_number:
            cycle = Cycle.objects.filter(cycle_number=cycle_number).first()
            payments = payments.filter(cycle=cycle)

        serializer = PaymentListSerializer(payments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipViewSet(SuccessMessageMixin, ModelViewSet):
    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action == 'list':
            group = self.request.query_params.get('group')
            qs = qs.filter(group=group)

        if self.action == 'destroy':
            qs = qs.select_related('group')

        return qs

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)

            # Append user to a payment list after saving membership.
            group = Group.objects.get(id=serializer.data['group'])
            cycle = Cycle.objects.filter(
                group=group, cycle_number=group.current_cycle).first()

            if cycle:
                append_member_to_payment_list(
                    group=group, cycle=cycle, user=self.request.user)

        except IntegrityError:
            raise PermissionDenied(
                _('This user is already a member of this group.'))

    def perform_destroy(self, instance):
        cycle = Cycle.objects.filter(
            group=instance.group, cycle_number=instance.group.current_cycle).first()

        payment_list = PaymentList.objects.get(
            cycle=cycle, group=instance.group, user=self.request.user)
        payment_list.delete()

        return super().perform_destroy(instance)

    @action(methods=['POST'], detail=False)
    def token(self, request, **kwargs):
        try:
            group = Group.objects.get(token=request.data['group_token'])
            membership = Membership.objects.create(
                user=request.user, group=group)
            serializer = self.get_serializer(membership)
        except Group.DoesNotExist:
            raise NotFound(_('Group with this token does not exist.'))
        except IntegrityError:
            raise PermissionDenied(
                _('This user is already a member of this group.'))

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def bulk_create(self, request, **kwargs):
        serializer = MembershipBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data
        group = Group.objects.get(id=data['group_id'])
        members = None

        with advisory_lock(f'membership-creation-{group.id}'):
            members = services.create_members_from_bulk(
                data['bulk_memberships'], group=group)

        members_serialized = MembershipSerializer(members, many=True)

        return Response(members_serialized.data, status=status.HTTP_201_CREATED)


class CycleViewSet(SuccessMessageMixin, ViewSet):
    serializer_class = CycleSerializer
    permission_classes = (IsAuthenticated,)
    resource_name = 'Cycle'

    def retrieve(self, request, pk=None):
        try:
            instance = Cycle.objects.get(pk=pk)
            serializer = self.serializer_class(instance)
        except Cycle.DoesNotExist:
            raise NotFound()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def set(self, request, **kwargs):
        current_cycle_number = 1
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            group = Group.objects.get(id=request.data['group'])
            cycle = Cycle.objects.filter(
                group=group).order_by('-cycle_number').first()

            # If the cycle date is a null value or the current date is before the end date.
            if cycle and (not cycle.end_date or datetime.now().date() < cycle.end_date):
                raise PermissionDenied(
                    _('Cannot create another cycle during an ongoing cycle.'))

            # If a cycle exists, increment the cycle number by 1
            if cycle:
                current_cycle_number = cycle.cycle_number + 1

        except Group.DoesNotExist:
            raise NotFound(_('Group does not exist.'))

        serializer.save(
            group=group, cycle_number=current_cycle_number)

        # Fetch all the member in the group.
        memberships = Membership.objects.filter(group=group)[::1]
        cycle = Cycle.objects.get(id=serializer.data['id'])

        generate_payment_list(
            start_date=serializer.data['start_date'], group=group, cycle=cycle, memberships=memberships)

        return Response(serializer.data, status=status.HTTP_200_OK)
