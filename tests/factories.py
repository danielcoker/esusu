from secrets import token_hex
from random import randint, choice

import factory


class Factory(factory.django.DjangoModelFactory):
    pass


class UserFactory(Factory):
    class Meta:
        model = 'users.User'

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(
        lambda obj: f'{obj.first_name}{obj.last_name}{randint(1, 1000)}@email.com')
    password = factory.PostGeneration(
        lambda obj, *args, **kwargs: obj.set_password(obj.first_name))
    is_active = True


class GroupFactory(Factory):
    class Meta:
        model = 'groups.Group'

    name = factory.Sequence(lambda n: f'Group {n}')
    description = factory.Sequence(lambda n: f'Group {n} description.')
    max_capacity = randint(1, 20)
    amount_to_save = choice([1000, 1500, 2000])
    owner = factory.SubFactory('tests.factories.UserFactory')
    token = token_hex(10).upper()


class MembershipFactory(Factory):
    class Meta:
        model = 'groups.Membership'

    user = factory.SubFactory('tests.factories.UserFactory')
    group = factory.SubFactory('tests.factories.GroupFactory')
    is_admin = False


class BankFactory(Factory):
    class Meta:
        model = 'transactions.Bank'

    account_name = factory.Faker('name')
    account_number = '0000000000'
    bank_code = '011'
    bank_name = 'First Bank of Nigeria'
    transfer_recipient = factory.Sequence(lambda n: f'RCP_t0ya41mp35flk4{n}.')
    is_default = False
    user = factory.SubFactory('tests.factories.UserFactory')
