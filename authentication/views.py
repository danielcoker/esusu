from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from base.mixins import SuccessMessageMixin

from .serializers import RegistrationSerializer


class AuthViewSet(SuccessMessageMixin, ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['POST'], detail=False)
    def register(self, request, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.success_message = 'User registered successfully.'

        return Response(serializer.data, status=status.HTTP_200_OK)
