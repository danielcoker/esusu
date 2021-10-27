from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from djmoney.models.fields import MoneyField

from base.models import TimestampedModel
from groups.models import Group, Cycle


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


class Transaction(TimestampedModel):
    SAVINGS = 'savings'
    PAYMENT = 'payment'
    PAYMENT_TYPE_CHOICES = [
        (SAVINGS, 'Savings'),
        (PAYMENT, 'Payment')
    ]

    PENDING = 'pending'
    SUCCESS = 'success'
    REVERSED = 'reversed'
    ABANDONED = 'abandoned'
    FAILED = 'failed'
    PAYMENT_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (REVERSED, 'reversed'),
        (ABANDONED, 'Abondoned'),
        (FAILED, 'Failed'),
    ]

    reference = models.CharField(
        max_length=255, verbose_name=_('transaction reference'))
    amount = MoneyField(max_digits=14, decimal_places=2,
                        default_currency='NGN', verbose_name=_('amount'))
    type = models.CharField(
        max_length=128, choices=PAYMENT_TYPE_CHOICES, verbose_name=_('payment type'))
    status = models.CharField(
        max_length=128, choices=PAYMENT_STATUS_CHOICES, verbose_name=_('payment status'))
    comments = models.TextField(
        blank=True, default='', verbose_name=_('comments'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return self.reference


class PaymentList(TimestampedModel):
    order = models.IntegerField(verbose_name=_('order'))
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='payment_list')
    cycle = models.ForeignKey(
        Cycle, on_delete=models.CASCADE, related_name='payment_list')
    payment_date = models.DateField(
        blank=True, null=True, verbose_name=_('payment date'))
    transaction = models.ForeignKey(
        Transaction, blank=True, null=True, on_delete=models.CASCADE, related_name='payment_list')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='payment_list')

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return str(self.payment_date)


class SavingsList(TimestampedModel):
    cycle = models.ForeignKey(
        Cycle, on_delete=models.CASCADE, related_name='savings_list')
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='savings_list')
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name='savings_list')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='savings_list')
