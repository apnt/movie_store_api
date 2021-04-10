from rest_framework import permissions


class IsSuperuser(permissions.BasePermission):

    def user_is_authenticated(self, request):
        return request.user and request.user.is_authenticated

    def user_is_superuser(self, request):
        return self.user_is_authenticated(request) and (request.user.is_staff or request.user.is_superuser)

    def has_permission(self, request, view):
        return self.user_is_authenticated(request) and self.user_is_superuser(request)