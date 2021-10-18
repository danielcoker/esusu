import secrets

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from base.mixins import SuccessMessageMixin
from base.permissions import IsOwnerOrReadOnly

from .models import Group
from .serializers import GroupSerializer


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
