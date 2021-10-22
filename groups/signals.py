from datetime import timedelta

from django.apps import apps


def get_cycle_end_date(start_date, member_count):
    """
    Get the end date of a cycle from its start date and the number of group members.

    :param start_date: The cycle start date.
    :param member_count: The number of members in the group.

    :return: The cycle end date.
    """
    return start_date + timedelta(days=member_count*7)


def set_end_date_for_membership(membership_instance):
    """
    Set the cycle end date for membership signals.

    :pram membership_instance: The membership instance.

    :return None
    """
    Cycle = apps.get_model('groups', 'Cycle')
    Membership = apps.get_model('groups', 'Membership')

    memberships = Membership.objects.filter(group=membership_instance.group.id)
    cycle = Cycle.objects.filter(group=membership_instance.group.id,
                                 cycle_number=membership_instance.group.current_cycle)

    end_date = get_cycle_end_date(
        cycle[0].start_date, memberships.count())

    cycle.update(end_date=end_date)


def membership_post_save(sender, instance, created, **kwargs):
    if not instance.group.current_cycle:
        return

    set_end_date_for_membership(instance)


def membership_post_delete(sender, instance, using, **kwargs):
    if not instance.group.current_cycle:
        return

    set_end_date_for_membership(instance)


def cycle_post_save(sender, instance, created, **kwargs):
    Cycle = apps.get_model('groups', 'Cycle')
    Membership = apps.get_model('groups', 'Membership')
    Group = apps.get_model('groups', 'Group')

    memberships = Membership.objects.filter(group=instance.group.id)

    end_date = get_cycle_end_date(
        instance.start_date, memberships.count())

    Cycle.objects.filter(id=instance.id).update(
        end_date=end_date, next_saving_date=instance.next_saving_date or instance.start_date)

    Group.objects.filter(id=instance.group.id).update(
        current_cycle=instance.cycle_number)
