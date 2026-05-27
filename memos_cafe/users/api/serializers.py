from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from memos_cafe.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "url"]
        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["email"] = user.email
        token["nombre"] = user.get_full_name() or user.email
        token["roles"] = list(user.groups.values_list("name", flat=True))
        return token