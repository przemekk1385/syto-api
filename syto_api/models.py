from django.contrib.auth.backends import get_user_model
from django.db import models

UserModel = get_user_model()


class AvailabilityPeriod(models.Model):

    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)


class AvailabilityHours(models.Model):

    day = models.DateField()
    hours = models.IntegerField()
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
