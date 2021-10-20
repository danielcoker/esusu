import secrets

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django_pglocks import advisory_lock

from base.mixins import SuccessMessageMixin
from base.permissions import IsOwnerOrReadOnly
from users.models import User

from .models import Group
from .serializers import GroupSerializer, MembershipSerializer, MembershipBulkSerializer
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


class MembershipViewSet(SuccessMessageMixin, ModelViewSet):
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
