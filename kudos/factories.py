import factory
from kudos.models import Company, Employee, UserKudosCounter


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.sequence(lambda c: "Company %d" % c)


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    company = CompanyFactory()
    username = factory.sequence(lambda c: "usname_ %d" % c)
    first_name = factory.sequence(lambda c: "user_first_ %d" % c)
    last_name = factory.sequence(lambda c: "user_second_ %d" % c)


class UserKudosCounterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserKudosCounter
