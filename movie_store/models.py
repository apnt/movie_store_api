from uuid import uuid4
from django.db import models
from django.conf import settings


class Genre(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Movie(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    title = models.CharField(max_length=255)
    year = models.PositiveSmallIntegerField()
    summary = models.TextField()
    director = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='movies', related_query_name='movie')


class Rental(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rentals',
                             related_query_name='rental')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='rentals', related_query_name='rental')
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True)
    returned = models.BooleanField(default=False)
    payment = models.FloatField(null=True, editable=False)
