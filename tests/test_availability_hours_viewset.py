import json
from datetime import date, timedelta

import pytest
from django.shortcuts import reverse

from syto_api.models import AvailabilityHours

TODAY = date.today()


@pytest.mark.parametrize(
    ("groups", "results_count"),
    [
        (["cottage_worker"], 5),
        (["cottage_worker", "foreman"], 15),
    ],
)
@pytest.mark.django_db
def test_list(groups, results_count, api_client, syto_user, syto_slot):
    user = syto_user(groups=groups)
    api_client.force_authenticate(user)

    for i in range(5):
        slot = syto_slot(
            day=TODAY - timedelta(days=i), is_open_for_cottage_workers=True
        )
        AvailabilityHours.objects.create(
            slot=slot,
            hours=8,
            user=syto_user(f"foo{i + 1}@bar.baz", groups=["cottage_worker"]),
        )
        AvailabilityHours.objects.create(
            slot=slot,
            hours=8,
            user=user,
        )
    for i in range(5, 10):
        AvailabilityHours.objects.create(
            slot=syto_slot(
                day=TODAY - timedelta(days=i), is_open_for_cottage_workers=True
            ),
            hours=8,
            user=syto_user(f"foo{i + 1}@bar.baz", groups=["cottage_worker"]),
        )

    response = api_client.get(reverse("syto_api:availability-hours-list"))

    assert response.status_code == 200
    assert len(response.data) == results_count


@pytest.mark.django_db
def test_create_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    payload = {
        "slot": syto_slot(is_open_for_cottage_workers=True).day,
        "hours": 8,
    }

    response = api_client.post(reverse("syto_api:availability-hours-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_create_failed(api_client, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    payload = {
        "slot": syto_slot(is_open_for_cottage_workers=True).day,
        "hours": 8,
    }

    response = api_client.post(reverse("syto_api:availability-hours-list"), payload)

    assert response.status_code == 403


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    availability = AvailabilityHours.objects.create(
        slot=syto_slot(is_open_for_cottage_workers=True),
        hours=8,
        user=user,
    )

    response = api_client.get(
        reverse("syto_api:availability-hours-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["hours"] == 8


@pytest.mark.django_db
def test_update_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    availability = AvailabilityHours.objects.create(
        slot=syto_slot(is_open_for_cottage_workers=True),
        hours=8,
        user=user,
    )

    response = api_client.patch(
        reverse("syto_api:availability-hours-detail", args=[availability.id]),
        data=json.dumps({"hours": 10}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["hours"] == 10


@pytest.mark.django_db
def test_update_failed(api_client, syto_user, syto_slot):
    user1 = syto_user("foo1@bar.baz", groups=["cottage_worker"])
    user2 = syto_user("foo2@bar.baz", groups=["cottage_worker"])
    api_client.force_authenticate(user1)

    availability = AvailabilityHours.objects.create(
        slot=syto_slot(is_open_for_cottage_workers=True),
        hours=8,
        user=user2,
    )

    response = api_client.patch(
        reverse("syto_api:availability-hours-detail", args=[availability.id]),
        data=json.dumps({"hours": 10}),
        content_type="application/json",
    )

    assert response.status_code == 403
