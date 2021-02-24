from rest_framework import serializers
from rest_framework.serializers import ValidationError

from syto_api.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "is_new",
            "evidence_number",
            "birth_date",
        ]

    def validate(self, data):
        email = data.get("email", None)
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)
        is_new = data.get("is_new", None)
        evidence_number = data.get("evidence_number", None)
        birth_date = data.get("birth_date", None)

        if (
            not email
            or first_name
            or last_name
            or is_new
            or evidence_number
            or birth_date
        ):
            raise ValidationError("Wszyskie pola muszą być wypełnione")
        return data
