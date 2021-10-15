from datetime import datetime, timedelta

import jwt

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils.translation import ugettext_lazy as _


from base.models import TimestampedModel


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None):
        """
        Create and return a user with a first_name, last_name, email, and password.
        """
        if first_name is None:
            raise TypeError('User must have a first name.')

        if last_name is None:
            raise TypeError('User must have a last name.')

        if email is None:
            raise TypeError('User must have an email address.')

        user = self.model(first_name=first_name,
                          last_name=last_name, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, password):
        """
        Create a user with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Super user must have a password.')

        user = self.create_user(first_name, last_name, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    is_active = models.BooleanField(_("active"), default=True,
                                    help_text=_("Designates whether this user should be treated as "
                                                "active. Unselect this instead of deleting accounts."))
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_(
                                       'Designates whether the user can log into the admin site.'),
                                   )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_full_name(self):
        """
        Returns the full name for the user.
        """
        return f'{self.first_name} {self.last_name}'

    def generate_jwt_token(self):
        """
        Generates a JSON Web Token (JWT) that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
