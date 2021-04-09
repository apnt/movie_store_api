from django.urls import re_path
from django.conf.urls import include
from .views import GenreViewSet, MovieViewSet, RentalViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'genres', GenreViewSet, basename="genres")
router.register(r'movies', MovieViewSet, basename="movies")
router.register(r'rentals', RentalViewSet, basename="rentals")

urlpatterns = [
    re_path(r'', include(router.urls)),
]