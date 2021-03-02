from typing import Callable

import pytest
from django.contrib.auth.backends import get_user_model
from rest_framework.test import APIClient

UserModel = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def syto_user() -> Callable:
    def make_syto_user(email: str, password: str = "FooBarBaz123") -> UserModel:
        return UserModel.objects.create(email=email, password=password)

    return make_syto_user
