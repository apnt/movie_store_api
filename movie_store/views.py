from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from common.paginations import MovieStorePagination
from .models import Genre, Movie, Rental
from .serializers import GenreSerializer, MovieSerializer, \
    CreateRentalSerializer, UpdateRentalSerializer, RentalSerializer
from .permissions import GenrePermissions, MoviePermissions, RentalPermissions
from .filters import YearFilter, GenreFilter, DirectorFilter, UserFilter, MovieFilter, StatusFilter
from . import api_schema


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    permission_classes = (IsAuthenticated, GenrePermissions)
    pagination_class = MovieStorePagination
    serializer_class = GenreSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    lookup_field = 'uuid'

    # filtering and ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    @extend_schema(**api_schema.list_genres)
    def list(self, request, *args, **kwargs):
        """Lists the genres."""
        return super().list(request, *args, **kwargs)

    @extend_schema(**api_schema.retrieve_genre)
    def retrieve(self, request, *args, **kwargs):
        """Retrieves a single genre."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**api_schema.create_genre)
    def create(self, request, *args, **kwargs):
        """Creates a new genre."""
        return super().create(request, *args, **kwargs)

    @extend_schema(**api_schema.partial_update_genre)
    def partial_update(self, request, *args, **kwargs):
        """Updates the data of a genre."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(**api_schema.destroy_genre)
    def destroy(self, request, *args, **kwargs):
        """Deletes a genre."""
        return super().destroy(request, *args, **kwargs)


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    permission_classes = (IsAuthenticated, MoviePermissions,)
    pagination_class = MovieStorePagination
    serializer_class = MovieSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    lookup_field = 'uuid'

    # filtering and ordering
    filter_backends = [SearchFilter, OrderingFilter, YearFilter, GenreFilter, DirectorFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'year']
    ordering = ['title']

    def get_queryset(self):
        queryset = Movie.objects.all()
        if self.action == 'get_user_library':
            user_active_rentals = self.request.user.rentals.filter(return_date=None)
            active_rentals_movies_ids = [rental.movie.id for rental in user_active_rentals]
            return queryset.filter(id__in=active_rentals_movies_ids)
        return self.filter_queryset(queryset)

    @extend_schema(**api_schema.list_movies)
    def list(self, request, *args, **kwargs):
        """Lists the movies."""
        return super().list(request, *args, **kwargs)

    @extend_schema(**api_schema.retrieve_movie)
    def retrieve(self, request, *args, **kwargs):
        """Retrieves a single movie."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**api_schema.create_movie)
    def create(self, request, *args, **kwargs):
        """Creates a new movie."""
        return super().create(request, *args, **kwargs)

    @extend_schema(**api_schema.partial_update_movie)
    def partial_update(self, request, *args, **kwargs):
        """Updates the data of a movie."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(**api_schema.destroy_movie)
    def destroy(self, request, *args, **kwargs):
        """Deletes a movie."""
        return super().destroy(request, *args, **kwargs)

    @extend_schema(**api_schema.library)
    @action(methods=['get'], detail=False, url_path='library', url_name='user-library')
    def get_user_library(self, request, *args, **kwargs):
        """Lists the movies for which the current user has an active rental (has rented it but not returned it)"""
        # call list with the library queryset
        return self.list(request, *args, **kwargs)


class RentalViewSet(ModelViewSet):
    queryset = Rental.objects.all()
    permission_classes = (IsAuthenticated, RentalPermissions)
    pagination_class = MovieStorePagination
    serializer_class = RentalSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    lookup_field = 'uuid'

    # filtering and ordering
    filter_backends = [SearchFilter, OrderingFilter, UserFilter, MovieFilter, StatusFilter]
    search_fields = ['movie__title']
    ordering_fields = ['movie__title', 'movie__year', 'rental_date', 'return_date', 'payment']
    ordering = ['rental_date']

    def get_queryset(self):
        """
        Gets the rentals.
        If the user has elevated permissions (staff or superuser), returns all rentals.
        If the user does not have elevated permissions, returns only his own rentals.
        """
        queryset = Rental.objects.all()
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            queryset = queryset.filter(user=self.request.user)
        return self.filter_queryset(queryset)

    def get_serializer_class(self):
        return {
            'create': CreateRentalSerializer,
            'partial_update': UpdateRentalSerializer
        }.get(self.action, super().get_serializer_class())

    def get_response_serializer_class(self):
        return self.serializer_class

    def get_response_serializer(self, *args, **kwargs):
        serializer_class = self.get_response_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    @extend_schema(**api_schema.list_rentals)
    def list(self, request, *args, **kwargs):
        """Lists the rentals."""
        return super().list(request, *args, **kwargs)

    @extend_schema(**api_schema.retrieve_rental)
    def retrieve(self, request, *args, **kwargs):
        """Retrieves a single rental."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**api_schema.create_rental)
    def create(self, request, *args, **kwargs):
        """Creates a new rental for the user who sends the request."""
        rental_data = dict(request.data, user=request.user.email)
        serializer = self.get_serializer(data=rental_data)
        serializer.is_valid(raise_exception=True)
        rental = self.perform_create(serializer)
        response_serializer = self.get_response_serializer(instance=rental)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(**api_schema.partial_update_rental)
    def partial_update(self, request, *args, **kwargs):
        """Updates the data of a rental."""
        instance = self.get_object()

        if instance.returned:
            return Response({'detail': 'This movie is already returned.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = self.perform_update(serializer)
        response_serializer = self.get_response_serializer(instance=updated_instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(**api_schema.destroy_rental)
    def destroy(self, request, *args, **kwargs):
        """Deletes a rental."""
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()
