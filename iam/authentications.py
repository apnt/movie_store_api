from rest_framework import authentication
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed


class JWTCookieAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_cookie = self.get_auth_cookie(request)
        if auth_cookie is None:
            return None

        auth_token = self.get_validated_token(auth_cookie)
        user = self.get_user(auth_token)
        return user, auth_token

    def get_auth_cookie(self, request):
        """
        Extracts the cookie/token containing the access token from the given request.
        """
        return request.COOKIES.get(api_settings.user_settings['AUTH_ACCESS_COOKIE'])

    def get_validated_token(self, raw_token):
        """
        Validates an encoded jwt and returns a validated token wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': 'Given token not valid for any token type',
            'messages': messages,
        })

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        user_model = get_user_model()
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except user_model.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user
