import json
from datetime import date
from functools import partial

import pytest
from django.shortcuts import reverse

from syto_api.models import AvailabilityPeriod

TODAY = date.today()


@pytest.mark.django_db
def test_list(api_client, syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    for i in range(5):
        slot = syto_slot(day=dt(timedelta_days=-i).date(), stationary_workers_limit=99)
        AvailabilityPeriod.objects.create(
            slot=slot,
            start=dt(hour=6),
            end=dt(hour=14),
            user=syto_user(f"foo{i + 1}@bar.baz", groups=["stationary_worker"]),
        )
        AvailabilityPeriod.objects.create(
            slot=slot,
            start=dt(hour=6),
            end=dt(hour=14),
            user=user,
        )
    for i in range(5, 10):
        AvailabilityPeriod.objects.create(
            slot=syto_slot(
                day=dt(timedelta_days=-i).date(), stationary_workers_limit=99
            ),
            start=dt(hour=6),
            end=dt(hour=14),
            user=syto_user(f"foo{i + 1}@bar.baz", groups=["stationary_worker"]),
        )

    response = api_client.get(reverse("syto_api:availability-period-list"))

    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.django_db
def test_create_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    slot = syto_slot(stationary_workers_limit=1)
    payload = {
        "slot": slot.day,
        "start": f"{slot.day} 06:00",
        "end": f"{slot.day} 14:00",
    }

    response = api_client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_create_failed(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    slot = syto_slot(stationary_workers_limit=1)
    payload = {
        "slot": slot.day,
        "start": f"{slot.day} 6:00",
        "end": f"{slot.day} 14:00",
    }

    response = api_client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 403


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_datetime, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    slot = syto_slot(stationary_workers_limit=1)
    availability = AvailabilityPeriod.objects.create(
        slot=slot,
        start=syto_datetime(hour=6),
        end=syto_datetime(hour=14),
        user=user,
    )

    response = api_client.get(
        reverse("syto_api:availability-period-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["start"] == f"{slot.day} 06:00"
    assert response.data["end"] == f"{slot.day} 14:00"


@pytest.mark.django_db
def test_update_ok(api_client, syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    slot = syto_slot(day=dt().date(), stationary_workers_limit=1)
    availability = AvailabilityPeriod.objects.create(
        slot=slot,
        start=dt(hour=6),
        end=dt(hour=14),
        user=user,
    )

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": f"{slot.day} 12:00"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["start"] == f"{slot.day} 06:00"
    assert response.data["end"] == f"{slot.day} 12:00"


@pytest.mark.django_db
def test_update_failed(api_client, syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    user1 = syto_user("foo1@bar.baz", groups=["stationary_worker"])
    user2 = syto_user("foo2@bar.baz", groups=["stationary_worker"])
    api_client.force_authenticate(user1)

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(day=dt().date(), stationary_workers_limit=1),
        start=dt(hour=6),
        end=dt(hour=14),
        user=user2,
    )

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": "12:00"}),
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("groups", "status"),
    [
        (["cottage_worker"], 403),
        (["stationary_worker"], 403),
        (["foreman"], 200),
    ],
)
@pytest.mark.django_db
def test_all(groups, status, api_client, syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    user = syto_user(groups=groups)
    api_client.force_authenticate(user)

    for i in range(5):
        slot = syto_slot(day=dt(timedelta_days=-i).date(), stationary_workers_limit=99)
        AvailabilityPeriod.objects.create(
            slot=slot,
            start=dt(hour=6),
            end=dt(hour=14),
            user=syto_user(f"foo{i + 1}@bar.baz", groups=["stationary_worker"]),
        )

    response = api_client.get(reverse("syto_api:availability-period-all"))

    assert response.status_code == status
