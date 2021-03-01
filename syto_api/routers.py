from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register("user", viewsets.UserViewSet, basename="user"),
