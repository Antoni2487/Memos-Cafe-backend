from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from memos_cafe.users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    groups = serializers.SerializerMethodField() 
    
    class Meta:
        model = User
        fields = ["id", "email", "name", "password", "is_active", "date_joined","groups"]
        read_only_fields = ["id", "date_joined"]

    def get_groups(self, obj):
        return [{"id": g.id, "name": g.name} for g in obj.groups.all()]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["email"] = user.email
        token["nombre"] = user.get_full_name() or user.email
        token["roles"] = list(user.groups.values_list("name", flat=True))
        return token