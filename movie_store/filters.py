from django.core.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from .models import Genre


# ----- Movie filters -----
class YearFilter(BaseFilterBackend):
    """Filtering by year"""
    def filter_queryset(self, request, queryset, view):
        year = request.query_params.get('year')
        if year is not None:
            try:
                year = int(year)
            except (ValueError, TypeError) as e:
                return queryset.none()
            return queryset.filter(year=year)
        return queryset


class GenreFilter(BaseFilterBackend):
    """
    Filtering by genre. Can filter by multiple genres (comma separated).
    When filtering by multiple genres, only the movies that are associated with all these genres will be listed.
    """
    def filter_queryset(self, request, queryset, view):
        queried_genres = request.query_params.get('genre')
        if queried_genres is not None:
            cleared_genres = [genre.strip() for genre in queried_genres.split(',')]
            genres = Genre.objects.none()
            # get the requested genres
            # case insensitive alternative to genres = Genre.objects.filter(name__in=cleared_genres)
            for g in cleared_genres:
                genres |= Genre.objects.filter(name__iexact=g)
            if len(genres) > 0:
                for genre in genres:
                    queryset = queryset.filter(id__in=genre.movies.all())
            else:
                queryset = queryset.none()
        return queryset


class DirectorFilter(BaseFilterBackend):
    """
    Filtering by director.
    """
    def filter_queryset(self, request, queryset, view):
        director = request.query_params.get('director')
        if director is not None:
            return queryset.filter(director=director)
        return queryset


# ----- Rental filters -----
class UserFilter(BaseFilterBackend):
    """
    Filtering by user.
    """
    def filter_queryset(self, request, queryset, view):
        user_uuid = request.query_params.get('user')
        if not (request.user.is_staff or request.user.is_superuser):
            return queryset
        if user_uuid is not None:
            try:
                return queryset.filter(user__uuid=user_uuid)
            except ValidationError:
                return queryset.none()
        return queryset


class MovieFilter(BaseFilterBackend):
    """
    Filtering by movie.
    """
    def filter_queryset(self, request, queryset, view):
        movie_uuid = request.query_params.get('movie')
        if movie_uuid is not None:
            try:
                return queryset.filter(movie__uuid=movie_uuid)
            except ValidationError:
                return queryset.none()
        return queryset


class StatusFilter(BaseFilterBackend):
    """
    Filtering by rental status.
    """
    def filter_queryset(self, request, queryset, view):
        status = request.query_params.get('status')
        if status == 'returned':
            return queryset.filter(returned=True)
        if status == 'active':
            return queryset.filter(returned=False)
        return queryset
