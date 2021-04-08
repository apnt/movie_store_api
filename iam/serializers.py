from drf_spectacular.utils import extend_schema_serializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


@extend_schema_serializer(exclude_fields=['refresh'])
class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
