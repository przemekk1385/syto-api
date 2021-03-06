from rest_access_policy import AccessPolicy
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AvailabilityHours, AvailabilityPeriod, Slot, User
from .serializers import (
    AvailabilityHoursSerializer,
    AvailabilityPeriodSerializer,
    SlotCreateSerializer,
    SlotSerializer,
    UserSerializer,
)


class UserAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["list"],
            "principal": ["group:foreman"],
            "effect": "allow",
        },
        {
            "action": ["create"],
            "principal": ["anonymous"],
            "effect": "allow",
        },
        {
            "action": ["retrieve", "update", "partial_update", "destroy"],
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
    def is_foreman(request, view, view_action: str) -> bool:
        return request.user.groups.filter(name="foreman").exists()

    @staticmethod
    def is_account_owner(request, view, view_action: str) -> bool:
        user = view.get_object()

        return user == request.user


class UserViewSet(viewsets.ModelViewSet):

    permission_classes = [UserAccessPolicy]
    serializer_class = UserSerializer
    queryset = User.objects.exclude(is_superuser=True)

    @action(detail=False, url_path="me", methods=["GET"])
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
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
            "action": ["list"],
            "principal": ["group:foreman", "group:cottage_worker"],
            "effect": "allow",
        },
        {
            "action": ["retrieve", "update", "partial_update", "destroy"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_owner",
        },
    ]


class AvailabilityHoursViewSet(viewsets.ModelViewSet):

    permission_classes = [AvailabilityHoursAccessPolicy]
    serializer_class = AvailabilityHoursSerializer
    queryset = AvailabilityHours.objects.all()

    def get_queryset(self):
        return (
            AvailabilityHours.objects.filter(user=self.request.user)
            if self.action == "list"
            else super().get_queryset()
        )


class AvailabilityPeriodAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["create"],
            "principal": ["group:stationary_worker"],
            "effect": "allow",
        },
        {
            "action": ["list"],
            "principal": ["group:foreman", "group:stationary_worker"],
            "effect": "allow",
        },
        {
            "action": ["retrieve", "update", "partial_update", "destroy"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_owner",
        },
        {
            "action": ["all"],
            "principal": ["group:foreman"],
            "effect": "allow",
        },
    ]


class AvailabilityPeriodViewSet(viewsets.ModelViewSet):

    permission_classes = [AvailabilityPeriodAccessPolicy]
    serializer_class = AvailabilityPeriodSerializer
    queryset = AvailabilityPeriod.objects.all()

    @action(detail=False, url_path="all", methods=["GET"])
    def all(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return (
            AvailabilityPeriod.objects.filter(user=self.request.user)
            if self.action == "list"
            else super().get_queryset()
        )


class SlotAccessPolicy(AccessPolicy):

    statements = [
        {
            "action": ["*"],
            "principal": ["group:foreman"],
            "effect": "allow",
        },
        {
            "action": ["list"],
            "principal": ["group:cottage_worker", "group:stationary_worker"],
            "effect": "allow",
        },
    ]


class SlotViewSet(viewsets.ModelViewSet):

    permission_classes = [SlotAccessPolicy]
    serializer_class = SlotSerializer
    queryset = Slot.objects.all()

    @action(detail=False, url_path="all", methods=["GET"])
    def all(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        if self.action != "list":
            pass
        elif self.request.user.is_stationary_worker:
            qs = Slot.objects.filter(stationary_workers_limit__gt=0)
        elif self.request.user.is_cottage_worker:
            qs = Slot.objects.filter(is_open_for_cottage_workers=True)
        else:
            qs = None

        return qs

    def get_serializer_class(self):
        return (
            SlotCreateSerializer
            if self.action == "create"
            else super().get_serializer_class()
        )
