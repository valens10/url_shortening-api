from rest_framework import serializers
from .models import CustomUser as User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "address",
            "gender",
            "is_active",
            "date_joined",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
        }

    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop("password", None)
        user = User.objects.create_user(**validated_data)  # Ensures password is hashed
        if password:
            user.set_password(password)
            user.save()
        return user

    def to_representation(self, instance):
        """Customize response to exclude sensitive fields"""
        data = super().to_representation(instance)
        data.pop("password", None)  # Ensure password is never exposed
        return data
