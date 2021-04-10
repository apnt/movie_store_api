from rest_framework import permissions
from common.permissions import IsSuperuser


class IsRenter(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class GenrePermissions(IsSuperuser):

    def has_permission(self, request, view):
        user_is_authenticated = self.user_is_authenticated(request)
        user_is_superuser = self.user_is_superuser(request)
        return {
            'create': user_is_superuser,
            'partial_update': user_is_superuser,
            'destroy': user_is_superuser,
        }.get(view.action, user_is_authenticated)


class MoviePermissions(IsSuperuser):

    def has_permission(self, request, view):
        user_is_authenticated = self.user_is_authenticated(request)
        user_is_superuser = self.user_is_superuser(request)
        return {
            'create': user_is_superuser,
            'partial_update': user_is_superuser,
            'destroy': user_is_superuser,
            'get_user_library': user_is_authenticated
        }.get(view.action, user_is_authenticated)


class RentalPermissions(IsSuperuser):

    def user_is_renter(self, request, obj):
        return obj.user == request.user

    def has_permission(self, request, view):
        user_is_authenticated = self.user_is_authenticated(request)
        user_is_superuser = self.user_is_superuser(request)
        return {
            'destroy': user_is_superuser
        }.get(view.action, user_is_authenticated)

    def has_object_permission(self, request, view, obj):
        user_is_authenticated = self.user_is_authenticated(request)
        user_is_superuser = self.user_is_superuser(request)
        user_is_renter = self.user_is_renter(request, obj)
        return {
            'create': user_is_authenticated,
            'retrieve': user_is_renter or user_is_superuser,
            'partial_update': user_is_renter or user_is_superuser,
            'destroy': user_is_superuser
        }.get(view.action, user_is_renter or user_is_superuser)
