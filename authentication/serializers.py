from rest_framework import serializers

from users.models import User
from .services import login


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True)

    # The client should not be able to send a token along with a registration request.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',
                  'password', 'token', 'created_at',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.token = user.generate_jwt_token()

        return user


class LoginSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(
        max_length=128, write_only=True, required=True)
    token = serializers.CharField(max_length=255, read_only=True)
    created_at = serializers.ReadOnlyField()

    def validate(self, data):
        authenticate_kwargs = {
            'email': data['email'],
            'password': data['password']
        }

        return login(**authenticate_kwargs)
