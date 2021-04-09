from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_serializer
from .models import Genre, Movie, Rental
from .logic import calculate_charge


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='movies-detail', format='html', lookup_field="uuid")
    genres = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Genre.objects.all(), default=[])

    class Meta:
        model = Movie
        fields = '__all__'


@extend_schema_serializer(exclude_fields=['user'])
class CreateRentalSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=get_user_model().objects.all())
    movie = serializers.SlugRelatedField(slug_field='uuid', queryset=Movie.objects.all())

    def validate(self, attrs):
        active_rental_data = {'user': attrs['user'], 'movie': attrs['movie'], 'return_date': None}
        active_rental_exists = Rental.objects.filter(**active_rental_data).exists()
        if active_rental_exists:
            raise ValidationError('This movie is already rented.', code='non_field_errors')
        return attrs

    class Meta:
        model = Rental
        exclude = ('id', 'return_date', 'payment')


@extend_schema_serializer(exclude_fields=['user'])
class UpdateRentalSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        instance = super().save()
        if self.validated_data['returned'] is True:
            instance.return_date = timezone.now()
            instance.payment = calculate_charge(instance)
            instance.save()
        return instance

    class Meta:
        model = Rental
        fields = ('returned',)


@extend_schema_serializer(exclude_fields=['user'])
class RentalSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', queryset=get_user_model().objects.all())
    movie = MovieSerializer()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.return_date is None:
            representation['fee'] = calculate_charge(instance)
            return representation
        return representation

    class Meta:
        model = Rental
        exclude = ('id', )