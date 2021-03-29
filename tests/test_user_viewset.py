import pytest
from django.shortcuts import reverse


@pytest.mark.django_db
def test_create_ok(api_client):
    payload = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
    }

    response = api_client.post(reverse("syto_api:user-list"), payload)

    assert response.status_code == 201


@pytest.mark.django_db
def test_create_forbidden(api_client, syto_user):
    user = syto_user()
    api_client.force_authenticate(user)

    response = api_client.post(reverse("syto_api:user-list"), {})

    assert response.status_code == 403


@pytest.mark.django_db
def test_update_account_owner(api_client, syto_user):
    user = syto_user()
    api_client.force_authenticate(user)

    response = api_client.patch(
        reverse("syto_api:user-detail", args=[user.id]),
        {"first_name": "Foo", "last_name": "Bar"},
    )

    assert response.status_code == 200
    assert response.data.get("first_name") == "Foo"
    assert response.data.get("last_name") == "Bar"


@pytest.mark.parametrize(
    ("groups", "status", "first_name", "last_name"),
    [
        (["foreman"], 200, "Foo", "Bar"),
        ([], 403, None, None),
    ],
)
@pytest.mark.django_db
def test_update_other_user(
    groups, status, first_name, last_name, api_client, syto_user
):
    user1 = syto_user("foo1@bar.baz", groups=groups)
    user2 = syto_user("foo2@bar.baz")
    api_client.force_authenticate(user1)

    response = api_client.patch(
        reverse("syto_api:user-detail", args=[user2.id]),
        {"first_name": "Foo", "last_name": "Bar"},
    )

    assert response.status_code == status
    assert response.data.get("first_name") == first_name
    assert response.data.get("last_name") == last_name


@pytest.mark.django_db
def test_me_ok(api_client, syto_user):
    user = syto_user()
    api_client.force_authenticate(user)

    response = api_client.get(reverse("syto_api:user-me"))

    assert response.status_code == 200
    assert response.data.get("email") == user.email


def test_me_forbidden(api_client):
    response = api_client.get(reverse("syto_api:user-me"))

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("groups", "status", "is_active"),
    [
        (["foreman"], 200, False),
        ([], 403, None),
    ],
)
@pytest.mark.django_db
def test_toggle_is_active(groups, status, is_active, api_client, syto_user):
    user = syto_user(groups=groups)
    api_client.force_authenticate(user)

    response = api_client.get(reverse("syto_api:user-toggle-is-active", args=[user.id]))

    assert response.status_code == status
    assert response.data.get("is_active") is is_active
