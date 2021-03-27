from datetime import date
from typing import Callable

import pytest
from django.contrib.auth.backends import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from syto_api.models import Slot

UserModel = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def syto_slot() -> Callable:
    def make_syto_slot(
        day: date = date.today(),
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
