from django.db.models import fields
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('token', 'current_cycle', 'owner',)
