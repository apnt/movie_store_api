from drf_spectacular.utils import OpenApiParameter
from .serializers import CustomTokenRefreshSerializer


# auth
login = {'responses': {200: {}}}
refresh = {'request': CustomTokenRefreshSerializer, 'responses': {200: {}}}
logout = {'responses': {200: {}}}

# users
list_users = {
    'parameters': [
        OpenApiParameter(name='order_by', description='Which field to use when ordering the results.',
                         type=str, enum=['date_joined', 'email', 'last_name', 'first_name', 'last_login'])
    ]
}
retrieve_user = {}
