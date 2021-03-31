from datetime import date, timedelta

import pytest
from django.shortcuts import reverse

from syto_api.models import AvailabilityHours, AvailabilityPeriod
from syto_api.views import availability_overview_list

TODAY = date.today()


@pytest.mark.django_db
def test_get(rf, syto_user, syto_slot):
    users = [
        syto_user("foo1@bar.baz", groups=["cottage_worker", "new_employee"]),
        syto_user("foo2@bar.baz", groups=["cottage_worker"]),
        syto_user("foo3@bar.baz", groups=["stationary_worker", "new_employee"]),
        syto_user("foo4@bar.baz", groups=["stationary_worker"]),
    ]

    for i in range(20):
        AvailabilityHours.objects.create(
            slot=syto_slot(TODAY - timedelta(days=i)), hours=8, user=users[0]
        )
        AvailabilityHours.objects.create(
            slot=syto_slot(TODAY - timedelta(days=i)), hours=8, user=users[1]
        )

    for i in range(10):
        AvailabilityPeriod.objects.create(
            slot=syto_slot(TODAY - timedelta(days=i)),
            start="6:00",
            end="14:00",
            user=users[2],
        )
        AvailabilityPeriod.objects.create(
            slot=syto_slot(TODAY - timedelta(days=i)),
            start="6:00",
            end="14:00",
            user=users[3],
        )

    request = rf.get(reverse("syto_api:total-availability-list"))

    response = availability_overview_list(request)

    assert response.status_code == 200
    assert len(response.data) == 20
    assert response.data[10]["cottage_hours"] == 16
    assert response.data[10]["cottage_workers"] == 2
    assert response.data[10]["stationary_hours"] == 0
    assert response.data[10]["stationary_workers"] == 0
    assert response.data[0]["cottage_hours"] == 16
    assert response.data[0]["cottage_workers"] == 2
    assert response.data[0]["stationary_hours"] == 16
    assert response.data[0]["stationary_workers"] == 2


def test_post(rf):
    payload = {
        "foo": "foo",
        "bar": "bar",
    }

    request = rf.post(reverse("syto_api:total-availability-list"), payload)

    response = availability_overview_list(request)

    assert response.status_code == 405
