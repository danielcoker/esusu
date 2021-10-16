from django.db import models
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name',
                  'full_name', 'email', 'created_at',)

    def get_full_name(self, obj):
        return obj.get_full_name() if obj else ''
