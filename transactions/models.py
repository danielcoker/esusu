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


class Card(TimestampedModel):
    reference = models.CharField(
        max_length=255, verbose_name=_('transaction reference'))
    authorization_code = models.CharField(
        max_length=255, verbose_name=_('authorization code'))
    card_type = models.CharField(max_length=128, verbose_name=_('card type'))
    last4 = models.CharField(max_length=4, verbose_name=_('last 4 digits'))
    exp_month = models.CharField(max_length=2, verbose_name=_('expiry month'))
    exp_year = models.CharField(max_length=4, verbose_name=_('expiry year'))
    bin = models.CharField(max_length=6, verbose_name=_('bin'))
    bank = models.CharField(max_length=255, verbose_name=_('bank'))
    channel = models.CharField(max_length=128, verbose_name=_('channel'))
    signature = models.CharField(max_length=255, verbose_name=_('signature'))
    reusable = models.BooleanField(verbose_name=_('reusuable card'))
    country_code = models.CharField(
        max_length=5, verbose_name=_('country code'))
    is_default = models.BooleanField(
        default=False, verbose_name=_('default bank'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='cards')

    def __str__(self):
        return self.bank
