from django.db.models import fields
from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Group, Membership


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('token', 'current_cycle', 'owner',)


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    group = GroupSerializer(required=True)

    class Meta:
        model = Membership
        fields = ('user', 'group',)


class _MembershipBulkSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)


class MembershipBulkSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    bulk_memberships = _MembershipBulkSerializer(many=True)
