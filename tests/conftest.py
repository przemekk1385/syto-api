from datetime import date
from typing import Callable, Union

import pytest
from dateutil import tz
from django.conf import settings
from django.contrib.auth.backends import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APIClient

from syto_api.models import Slot

UserModel = get_user_model()

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def syto_slot() -> Callable:
    def make_syto_slot(
        day: Union[date, str] = TODAY,
        stationary_workers_limit: int = None,
        is_open_for_cottage_workers: bool = None,
    ) -> Slot:
        return Slot.objects.get_or_create(
            day=day,
            stationary_workers_limit=stationary_workers_limit,
            is_open_for_cottage_workers=is_open_for_cottage_workers,
        )[0]

    return make_syto_slot


@pytest.fixture
def syto_user() -> Callable:
    def make_syto_user(
        email: str = "foo@bar.baz", password: str = "FooBarBaz123", groups: list = None
    ) -> UserModel:
        groups = groups or []

        user = UserModel.objects.create(email=email, password=password, is_active=True)
        user.groups.set(
            [Group.objects.get_or_create(name=group_name)[0] for group_name in groups]
        )
        return user

    return make_syto_user


@pytest.fixture
def syto_datetime() -> Callable:
    def make_syto_datetime(
        year: int = TODAY.year,
        month: int = TODAY.month,
        day: int = TODAY.day,
        hour: int = 0,
        minute: int = 0,
        timedelta_days: int = 0,
    ) -> timezone.datetime:
        return timezone.datetime(
            year, month, day, hour, minute, 0, tzinfo=tz
        ) + timezone.timedelta(days=timedelta_days)

    return make_syto_datetime
