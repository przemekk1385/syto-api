from rest_access_policy import AccessPolicy
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AvailabilityHours, AvailabilityPeriod, Slot, User
from .serializers import (
    AvailabilityHoursSerializer,
    AvailabilityPeriodSerializer,
    SlotSerializer,
    UserSerializer,
)


class UserAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["create"],
            "principal": ["anonymous"],
            "effect": "allow",
        },
        {
            "action": ["retrieve", "update", "partial_update", "delete"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_foreman or is_account_owner",
        },
        {"action": ["me"], "principal": ["authenticated"], "effect": "allow"},
        {
            "action": ["toggle_is_active"],
            "principal": ["group:foreman"],
            "effect": "allow",
        },
    ]

    @staticmethod
    def is_foreman(request, view, action: str) -> bool:
        return request.user.groups.filter(name="foreman").exists()

    @staticmethod
    def is_account_owner(request, view, action: str) -> bool:
        user = view.get_object()

        return user == request.user


class UserViewSet(viewsets.ModelViewSet):

    permission_classes = [UserAccessPolicy]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, url_path="me", methods=["GET"])
    def me(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path="toggle_is_active", methods=["GET"])
    def toggle_is_active(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()

        return Response({"is_active": instance.is_active}, status=status.HTTP_200_OK)


class AvailabilityHoursAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["create"],
            "principal": ["group:cottage_worker"],
            "effect": "allow",
        },
        {
            "action": ["retrieve", "update", "partial_update", "delete"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_owner",
        },
    ]


class AvailabilityHoursViewSet(viewsets.ModelViewSet):

    permission_classes = [AvailabilityHoursAccessPolicy]
    serializer_class = AvailabilityHoursSerializer
    queryset = AvailabilityHours.objects.all()


class AvailabilityPeriodAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["create"],
            "principal": ["group:stationary_worker"],
            "effect": "allow",
        },
        {
            "action": ["retrieve", "update", "partial_update", "delete"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_owner",
        },
    ]


class AvailabilityPeriodViewSet(viewsets.ModelViewSet):

    permission_classes = [AvailabilityPeriodAccessPolicy]
    serializer_class = AvailabilityPeriodSerializer
    queryset = AvailabilityPeriod.objects.all()


class SlotAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["*"],
            "principal": ["group:foreman"],
            "effect": "allow",
        },
        {
            "action": ["list", "retrieve"],
            "principal": ["group:cottage_worker", "group:stationary_worker"],
            "effect": "allow",
        },
    ]


class SlotViewSet(viewsets.ModelViewSet):

    permission_classes = [SlotAccessPolicy]
    serializer_class = SlotSerializer
    queryset = Slot.objects.all()
