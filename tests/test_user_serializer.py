from datetime import date

import pytest
from dateutil.relativedelta import relativedelta

from syto_api.serializers import UserSerializer

OF_AGE = date.today() - relativedelta(years=18)


@pytest.mark.django_db
def test_valid_data_new_stationary_worker():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_new": True,
        "date_of_birth": OF_AGE,
        "phone_number": "+48129999999",
        "address": "foo 123, bar",
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"new_employee", "stationary_worker"}


@pytest.mark.django_db
def test_valid_data_old_stationary_worker():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"stationary_worker"}


@pytest.mark.django_db
def test_valid_data_new_cottage_worker():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_new": True,
        "is_cottage": True,
        "date_of_birth": OF_AGE,
        "phone_number": "+48129999999",
        "address": "foo 123, bar",
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"new_employee", "cottage_worker"}


@pytest.mark.django_db
def test_valid_data_old_cottage_employee():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_cottage": True,
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"cottage_worker"}


@pytest.mark.parametrize(
    ("field", "extra_data", "error_message"),
    [
        (
            "date_of_birth",
            {
                "date_of_birth": date.today() - relativedelta(years=17),
                "phone_number": "+48129999999",
                "address": "foo 123, bar",
            },
            "User must be of age.",
        ),
        (
            "date_of_birth",
            {"phone_number": "+48129999999", "address": "foo 123, bar"},
            "This field is required when 'is_new' flag is True.",
        ),
        (
            "phone_number",
            {"date_of_birth": OF_AGE, "address": "foo 123, bar"},
            "This field is required when 'is_new' flag is True.",
        ),
        (
            "address",
            {"date_of_birth": OF_AGE, "phone_number": "+48129999999"},
            "This field is required when 'is_new' flag is True.",
        ),
    ],
)
@pytest.mark.django_db
def test_invalid_data_new_employee(extra_data, field, error_message):
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_new": True,
        **extra_data,
    }

    serializer = UserSerializer(data=data)

    assert not serializer.is_valid()
    assert len(serializer.errors) == 1
    assert serializer.errors.get(field, [""])[0] == error_message


@pytest.mark.django_db
def test_invalid_data_old_employee():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
    }

    serializer = UserSerializer(data=data)

    assert not serializer.is_valid()
    assert len(serializer.errors) == 1
