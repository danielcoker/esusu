from django.db import transaction


@transaction.atomic
def save_in_bulk(instances, **save_options):
    """
    Save a list of model instances.

    :params instances: List of model instances.
    :params save_options: Additional options to use when saving each instance.
    """
    for instance in instances:
        instance.save(**save_options)
