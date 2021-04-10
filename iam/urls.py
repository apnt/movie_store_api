from django.urls import re_path
from django.conf.urls import include
from django.urls import path
from .views import AuthView, UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename="users")

urlpatterns = [
    path('auth/', AuthView.as_view(), name='authenticate'),
    re_path(r'', include(router.urls)),
]
