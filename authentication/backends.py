import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this meanas we know authentication will fail. An example
                    of this is when the request does not include a token in the headers.

        2) `(user, token)` - We return a user/token combination when authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything
                            We simply raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest."""
        request.user = None

        #  `auth_header` should be an array with two elements. 1) the name of
        # the authentication header ( in this case, "Bearer") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authemticate.
            return None
        elif len(auth_header) > 2:
            # Invalid token header. The token string should not contain spaces.
            # Do not attempt to authenticate.
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expect. Do not attempt to
            # authenticate.
            return None

        # By now, we are sure there is a change that authenticate will
        # succeed. We delegate the actual credientials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
        except:
            raise exceptions.AuthenticationFailed(
                'Invalid authentication. Could not decode token.')

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'No user matching this token was found.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                'This user has been deactivated.')

        return (user, token)
