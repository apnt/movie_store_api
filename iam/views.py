from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema
from common.permissions import IsSuperuser
from .authentications import JWTCookieAuthentication
from .serializers import CustomTokenRefreshSerializer, CustomUserSerializer
from .models import CustomUser


class AuthView(GenericAPIView):
    """View that implements the user authentication (login, refresh, logout)"""
    authentication_classes = (JWTCookieAuthentication,)
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Return the class to use for the serializer."""
        if self.request.method == 'PATCH':
            return CustomTokenRefreshSerializer
        return TokenObtainPairSerializer

    @extend_schema(responses={200: {}})
    def post(self, request, *args, **kwargs):
        """
        User login with email and password.
        In case of success sets the access and refresh cookies and returns 200.
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response('Token is not valid.', status=status.HTTP_400_BAD_REQUEST)
        except ValueError:  # for example if we have wrong signing and verifying keys
            return Response('Error in token.', status=status.HTTP_400_BAD_REQUEST)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(**self.access_cookie(serializer.validated_data['access']))
        response.set_cookie(**self.refresh_cookie(serializer.validated_data['refresh']))
        return response

    @extend_schema(request=CustomTokenRefreshSerializer, responses={200: {}})
    def patch(self, request, *args, **kwargs):
        """Refresh access token and update in access cookie using the refresh token in the refresh cookie."""
        refresh_token = request.COOKIES.get(api_settings.user_settings['AUTH_REFRESH_COOKIE'])
        if refresh_token is None:
            raise NotAuthenticated
        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response('Token is not valid.', status=status.HTTP_400_BAD_REQUEST)
        except ValueError:  # for example if we have wrong signing and verifying keys
            return Response('Error in token.', status=status.HTTP_400_BAD_REQUEST)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(**self.access_cookie(serializer.validated_data['access']))
        return response

    @extend_schema(responses={200: {}})
    def delete(self, request, *args, **kwargs):
        """User logout. Clears the access and refresh cookies."""
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie(key=api_settings.user_settings['AUTH_ACCESS_COOKIE'])
        response.delete_cookie(key=api_settings.user_settings['AUTH_REFRESH_COOKIE'])
        return response

    @staticmethod
    def access_cookie(value):
        return {
            'key': api_settings.user_settings['AUTH_ACCESS_COOKIE'],
            'value': value,
            'expires': (datetime.utcnow() + api_settings.ACCESS_TOKEN_LIFETIME),
            'httponly': True,
        }

    @staticmethod
    def refresh_cookie(value):
        return {
            'key': api_settings.user_settings['AUTH_REFRESH_COOKIE'],
            'value': value,
            'expires': (datetime.utcnow() + api_settings.REFRESH_TOKEN_LIFETIME),
            'httponly': True,
        }


class UserViewSet(ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    authentication_classes = (JWTCookieAuthentication,)
    permission_classes = (IsAuthenticated, IsSuperuser,)
    serializer_class = CustomUserSerializer
    lookup_field = 'uuid'

    # filtering and ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_name', 'first_name', 'last_login']
    ordering = ['last_name', 'first_name']
