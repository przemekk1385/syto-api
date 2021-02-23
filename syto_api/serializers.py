from rest_framework import serializers

from syto_api.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:

        fields = "__all__"
        model = User
