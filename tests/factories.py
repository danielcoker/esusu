from random import randint

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
