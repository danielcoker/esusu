from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from djmoney.models.fields import MoneyField

from base.models import TimestampedModel


class Group(TimestampedModel):
    name = models.CharField(_('name'), max_length=128)
    description = models.TextField(
        null=True, blank=True, verbose_name=_('description'))
    max_capacity = models.IntegerField(verbose_name=_(
        'max capacity'), validators=[MinValueValidator(0)])
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Membership')
    current_cycle = models.IntegerField(
        null=True, blank=True, verbose_name=_('current cycle'))
    amount_to_save = MoneyField(max_digits=14, decimal_places=2,
                                default_currency='NGN', verbose_name=_('amount to save'))
    # Sharable unique token for a group
    token = models.CharField(max_length=60, unique=True, default=None,
                             verbose_name=_("token"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              related_name='owned_groups', verbose_name=_('owner'), on_delete=models.SET_NULL)
    is_searchable = models.BooleanField(
        default=True, verbose_name=_('searchable group'))

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='memberships')
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='memberships')
    is_admin = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        unique_together = ('user', 'group',)
        ordering = ['-created_at']


class Cycle(models.Model):
    cycle_number = models.IntegerField(
        blank=True, null=True, verbose_name=_('cycle number'))
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(
        blank=True, null=True, verbose_name=_('end date'))
    next_saving_date = models.DateField(
        blank=True, null=True, verbose_name=_('next saving date'))
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='cycles')
