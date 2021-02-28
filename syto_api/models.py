from django.contrib.auth.backends import get_user_model
from django.db import models
from django.db.models import ExpressionWrapper, F

UserModel = get_user_model()


class AvailabilityPeriodQuerySet(models.QuerySet):
    def with_timedelta(self):
        timedelta_expression = ExpressionWrapper(
            F("end") - F("start"), output_field=models.DurationField()
        )
        return self.annotate(timedelta=timedelta_expression)


class AvailabilityPeriod(models.Model):

    objects = AvailabilityPeriodQuerySet.as_manager()

    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)


class AvailabilityHours(models.Model):

    day = models.DateField()
    hours = models.IntegerField()
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
