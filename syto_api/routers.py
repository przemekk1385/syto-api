from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register("user", viewsets.UserViewSet, basename="user")
router.register("slot", viewsets.SlotViewSet, basename="slot")
router.register(
    "availability/hours",
    viewsets.AvailabilityHoursViewSet,
    basename="availability-hours",
)
router.register(
    "availability/period",
    viewsets.AvailabilityPeriodViewSet,
    basename="availability-period",
)
