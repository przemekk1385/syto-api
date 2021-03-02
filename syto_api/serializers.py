from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import AvailabilityHours, AvailabilityPeriod, User


class UserSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    groups = serializers.SlugRelatedField("name", many=True, read_only=True)

    evidence_number = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)

    # extra field that doesn't go to db
    is_new = serializers.BooleanField(required=False, write_only=True)
    is_cottage = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "groups",
            "evidence_number",
            "date_of_birth",
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

            evidence_number = self.initial_data.get("evidence_number")
            if not evidence_number:
                errors["evidence_number"] = [
                    "This field is required when 'is_new' flag is True."
                ]

            date_of_birth = self.initial_data.get("date_of_birth")
            if not date_of_birth:
                errors["date_of_birth"] = [
                    "This field is required when 'is_new' flag is True."
                ]

            if errors:
                raise serializers.ValidationError(errors)

        return attrs


class AvailabilityHoursSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityHours

    @staticmethod
    def validate_hours(val, *args, **kwargs):
        if val > 16:
            raise serializers.ValidationError(
                ["Maximum allowed number of hours is 16."]
            )

        return val


class AvailabilityPeriodSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityPeriod

    def validate(self, attrs):
        errors = {"non_field_errors": []}

        if attrs["start"].date() != attrs["end"].date():
            errors["non_field_errors"].append("Start and end must be at the same day.")

        if (attrs["end"] - attrs["start"]).seconds // 3600 > 16:
            errors["non_field_errors"].append("Maximum allowed number of hours is 16.")

        if (attrs["end"] - attrs["start"]).seconds % 3600:
            errors["non_field_errors"].append("Only full number of hours is allowed.")

        if errors["non_field_errors"]:
            raise serializers.ValidationError(errors)

        return attrs
