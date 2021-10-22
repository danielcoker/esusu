from django.apps import AppConfig, apps
from django.db.models import signals

from . import signals as handlers


class GroupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'groups'

    def ready(self):
        signals.post_save.connect(handlers.cycle_post_save,
                                  sender=apps.get_model('groups', 'Cycle'),
                                  dispatch_uid='cycle_post_save')
        signals.post_save.connect(handlers.membership_post_save,
                                  sender=apps.get_model(
                                      'groups', 'Membership'),
                                  dispatch_uid='membership_post_save')
        signals.post_delete.connect(handlers.membership_post_delete,
                                    sender=apps.get_model(
                                        'groups', 'Membership'),
                                    dispatch_uid='membership_post_delete')
