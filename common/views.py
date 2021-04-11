from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import exceptions as drf_exceptions


def custom_exception_handler(exc, context):

    # 401 unauthenticated responses
    if isinstance(exc, drf_exceptions.AuthenticationFailed):
        error_response = {'detail': 'Invalid credentials.'}
        return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, drf_exceptions.NotAuthenticated):
        error_response = {'detail': 'Authentication credentials were not provided.'}
        return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

    # 403 permission denied responses
    if isinstance(exc, drf_exceptions.PermissionDenied):
        error_response = {'detail': 'You do not have permission to perform this action.'}
        return Response(error_response, status=status.HTTP_403_FORBIDDEN)

    # if none of the above cases checked true, call the default drf exception handler
    response = exception_handler(exc, context)
    return response
