from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from base.models import TimestampedModel


class Bank(TimestampedModel):
    account_name = models.CharField(
        max_length=255, verbose_name=(_('account name')))
    account_number = models.CharField(
        max_length=20, verbose_name=_('account number'))
    bank_code = models.CharField(max_length=10, verbose_name=_('bank code'))
    bank_name = models.CharField(max_length=255, verbose_name=_('bank name'))
    transfer_recipient = models.CharField(
        max_length=255, verbose_name=_('transfer_recipient'))
    is_default = models.BooleanField(
        default=False, verbose_name=_('default bank'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='banks')

    def __str__(self):
        return self.account_name
