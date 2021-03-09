import pytest
from django.shortcuts import reverse


@pytest.mark.django_db
def test_toggle_is_active(api_client, syto_user):
    user = syto_user("foo@bar.baz")
    is_active = user.is_active

    response = api_client.get(reverse("syto_api:user-toggle-is-active", args=[user.id]))

    assert response.status_code == 200
    assert response.data["is_active"] != is_active
