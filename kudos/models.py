from django.db.models.signals import post_save
import arrow
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import PermissionDenied
from djangoProject import settings
from djangoProject.settings import DEFAULT_KUDOS_PER_WEEK


class Company(models.Model):
    name = models.CharField(max_length=100)


class Employee(AbstractUser):
    company = models.ForeignKey(to=Company, related_name="employees", on_delete=models.CASCADE)


class UserKudosCounter(models.Model):
    user_id = models.OneToOneField(to=Employee, on_delete=models.CASCADE)
    counter = models.PositiveSmallIntegerField(default=DEFAULT_KUDOS_PER_WEEK)
    updated_at = models.DateTimeField(auto_now=True)

    def reset_counter(self):
        UserKudosCounter.objects.filter(user_id=self.user_id).update(counter=DEFAULT_KUDOS_PER_WEEK)

    def update_counter(self):
        self.counter = self.counter - 1
        self.save()


def update_counter(sender, instance, **kwargs):
    UserKudosCounter.objects.get(user_id=instance.from_id).update_counter()


class Kudos(models.Model):
    from_id = models.ForeignKey(to=Employee, related_name="kudos_given", on_delete=models.CASCADE)
    to_id = models.ForeignKey(to=Employee, related_name="kudos_received", on_delete=models.CASCADE)
    message = models.CharField(null=True, blank=False, max_length=200)
    created_at = models.DateTimeField(auto_now=True)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        user_kudos_info = UserKudosCounter.objects.get(user_id=self.from_id)
        last_given_kudos_date = arrow.get(user_kudos_info.updated_at, tzinfo=settings.TIME_ZONE)
        now = arrow.now(tz=settings.TIME_ZONE)
        start_of_this_week, end_of_this_week = now.span('week')

        # Check if it's a new week
        if start_of_this_week <= last_given_kudos_date <= end_of_this_week:
            if user_kudos_info.counter == 0:
                raise PermissionDenied(detail="You have exhausted quota for this week")
        else:
            user_kudos_info.reset_counter()
        super(Kudos, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                update_fields=update_fields)


post_save.connect(update_counter, sender=Kudos)
