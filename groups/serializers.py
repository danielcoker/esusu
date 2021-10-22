from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Group, Membership, Cycle


class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(required=False, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('token', 'current_cycle', 'owner',)


class MembershipSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    group_token = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ('id', 'full_name', 'email', 'group_name', 'group_token', 'is_owner',
                  'is_admin', 'group', 'user', 'created_at')
        read_only_fields = ('user', 'is_admin', 'is_owner', 'full_name',)

    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj and obj.user else ''

    def get_email(self, obj):
        return obj.user.email if obj and obj.user else ''

    def get_group_name(self, obj):
        return obj.group.name if obj and obj.group else ''

    def get_group_token(self, obj):
        return obj.group.token if obj and obj.group else ''

    def get_is_owner(self, obj):
        return (obj and obj.user_id and obj.group_id and obj.group.owner_id and
                obj.user_id == obj.group.owner_id)


class _MembershipBulkSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)


class MembershipBulkSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    bulk_memberships = _MembershipBulkSerializer(many=True)


class CycleSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Cycle
        fields = ('cycle_number', 'start_date',
                  'end_date', 'next_saving_date', 'group',)
        read_only_fields = ('cycle_number', 'end_date',
                            'next_saving_date', 'group',)
