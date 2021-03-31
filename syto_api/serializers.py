from datetime import timedelta

from django.contrib.auth.models import Group
from django.db.models import Q
from phonenumber_field import serializerfields
from rest_framework import serializers

from .models import AvailabilityHours, AvailabilityPeriod, Slot, User


class UserSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField(read_only=True)
    groups = serializers.SlugRelatedField("name", many=True, read_only=True)

    date_of_birth = serializers.DateField(allow_null=True, required=False)
    phone_number = serializerfields.PhoneNumberField(
        allow_blank=True, allow_null=True, required=False
    )
    address = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    # extra field that doesn't go to db
    is_new = serializers.BooleanField(required=False, write_only=True)
    is_cottage = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "groups",
            "date_of_birth",
            "phone_number",
            "address",
            "is_new",
            "is_cottage",
        ]

    @staticmethod
    def _get_groups():
        return (
            group
            for group, _ in (
                Group.objects.get_or_create(name=name)
                for name in ("new_employee", "stationary_worker", "cottage_worker")
            )
        )

    def create(self, validated_data):
        is_new = validated_data.pop("is_new", None)
        is_cottage = validated_data.pop("is_cottage", None)

        instance = super().create(validated_data)

        new_employee, stationary_worker, cottage_worker = self._get_groups()

        if is_new:
            instance.groups.add(new_employee)

        if is_cottage:
            instance.groups.add(cottage_worker)
        else:
            instance.groups.add(stationary_worker)

        return instance

    def validate(self, attrs):
        if attrs.get("is_new"):
            errors = {}

            for key in ["date_of_birth", "phone_number", "address"]:
                value = self.initial_data.get(key)
                if not value:
                    errors[key] = ["This field is required when 'is_new' flag is True."]

            if errors:
                raise serializers.ValidationError(errors)

        return attrs


class AvailabilityHoursSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:

        fields = "__all__"
        model = AvailabilityHours

    def validate(self, attrs):
        if self.instance:
            attrs.setdefault("slot", self.instance.slot)
            attrs.setdefault("user", self.instance.user)

        errors = {"slot": [], "user": []}
        slot, user = (
            attrs["slot"],
            attrs["user"],
        )

        if (
            slot.availabilityhours_set.exclude(id=getattr(self.instance, "id", None))
            .filter(user=user)
            .exists()
        ):
            errors["user"].append("Worker can sign up only once for a day.")

        errors = {k: v for k, v in errors.items() if v}
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @staticmethod
    def validate_hours(val, *args, **kwargs):
        if val > 16:
            raise serializers.ValidationError(
                ["Maximum allowed number of hours is 16."]
            )

        return val

    @staticmethod
    def validate_slot(val, *args, **kwargs):
        errors = []

        if not val.is_open_for_cottage_workers:
            errors.append("Cannot sign up for a non-open day.")

        if errors:
            raise serializers.ValidationError(errors)

        return val


class AvailabilityPeriodSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:

        fields = "__all__"
        model = AvailabilityPeriod

    def validate(self, attrs):
        if self.instance:
            attrs.setdefault("start", self.instance.start)
            attrs.setdefault("end", self.instance.end)
            attrs.setdefault("slot", self.instance.slot)
            attrs.setdefault("user", self.instance.user)

        errors = {"non_field_errors": [], "slot": [], "user": []}
        start, end, slot, user = (
            attrs["start"],
            attrs["end"],
            attrs["slot"],
            attrs["user"],
        )

        td = timedelta(hours=end.hour, minutes=end.minute) - timedelta(
            hours=start.hour, minutes=start.minute
        )
        if td.days >= 0 and td.seconds // 3600 > 16:
            errors["non_field_errors"].append("Maximum allowed number of hours is 16.")

        if start >= end:
            errors["non_field_errors"].append("End must be after start.")

        if start.minute != end.minute:
            errors["non_field_errors"].append("Only full number of hours is allowed.")

        if (
            slot.availabilityperiod_set.exclude(id=getattr(self.instance, "id", None))
            .filter(user=user)
            .exists()
        ):
            errors["user"].append("Worker can sign up only once for a day.")

        errors = {k: v for k, v in errors.items() if v}
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    @staticmethod
    def validate_slot(val, *args, **kwargs):
        errors = []

        if not val.stationary_workers_limit:
            errors.append("Cannot sign up for a non-open day.")

        if val.availabilityperiod_set.count() == val.stationary_workers_limit:
            errors.append("Limit of signed up workers reached.")

        if errors:
            raise serializers.ValidationError(errors)

        return val


class SlotCreateSerializer(serializers.ModelSerializer):
    class Meta:

        fields = "__all__"
        model = Slot


class SlotSerializer(SlotCreateSerializer):

    day = serializers.DateField(read_only=True)


class UserBaseSerializer(serializers.BaseSerializer):
    def create(self, validated_data):
        raise NotImplementedError("UserBaseSerializer is read-only.")

    def update(self, instance, validated_data):
        raise NotImplementedError("UserBaseSerializer is read-only.")

    def to_internal_value(self, data):
        raise NotImplementedError("UserBaseSerializer is read-only.")

    def to_representation(self, instance):
        return {
            "first_name": instance.first_name or "",
            "last_name": instance.last_name or "",
            "groups": list(instance.groups.values_list("name", flat=True)),
        }


class AvailabilityOverviewBaseSerializer(serializers.BaseSerializer):
    def create(self, validated_data):
        raise NotImplementedError("AvailabilityOverviewBaseSerializer is read-only.")

    def update(self, instance, validated_data):
        raise NotImplementedError("AvailabilityOverviewBaseSerializer is read-only.")

    def to_internal_value(self, data):
        raise NotImplementedError("AvailabilityOverviewBaseSerializer is read-only.")

    def to_representation(self, instance):
        qs = User.objects.filter(
            Q(availabilityhours__slot=instance.day)
            | Q(availabilityperiod__slot=instance.day)
        )
        serializer = UserBaseSerializer(qs, many=True)

        return {
            "day": instance.day,
            "cottage_hours": instance.cottage_hours,
            "cottage_workers": instance.cottage_workers,
            "stationary_hours": instance.stationary_hours,
            "stationary_workers": instance.stationary_workers,
            "workers": serializer.data,
        }
