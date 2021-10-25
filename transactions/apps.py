from django.apps import AppConfig, apps
from django.db.models import signals

from . import signals as handlers


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def ready(self) -> None:
        signals.post_save.connect(handlers.card_post_save,
                                  sender=apps.get_model(
                                      'transactions', 'Card'),
                                  dispatch_uid='card_post_save')
