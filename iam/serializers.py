from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .models import CustomUser


@extend_schema_serializer(exclude_fields=['refresh'])
class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ('id', )
