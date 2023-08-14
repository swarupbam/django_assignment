from django.contrib.auth.models import AbstractUser
from django.db import models
from djangoProject.settings import DEFAULT_KUDOS_PER_WEEK


class Company(models.Model):
    name = models.CharField(max_length=100)


class Employee(AbstractUser):
    company = models.ForeignKey(to=Company, related_name="employees", on_delete=models.CASCADE)


class UserKudosCounter(models.Model):
    user_id = models.OneToOneField(to=Employee, on_delete=models.CASCADE)
    counter = models.PositiveSmallIntegerField(default=DEFAULT_KUDOS_PER_WEEK)
    updated_at = models.DateTimeField(auto_now=True)


class Kudos(models.Model):
    from_id = models.ForeignKey(to=Employee, related_name="kudos_given", on_delete=models.CASCADE)
    to_id = models.ForeignKey(to=Employee, related_name="kudos_received", on_delete=models.CASCADE)
    message = models.CharField(null=True, blank=False, max_length=200)
    created_at = models.DateTimeField(auto_now=True)
