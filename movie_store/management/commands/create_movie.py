from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a movie in db'

    def handle(self, *args, **options):
        movie_model = apps.get_model('movie_store', 'Movie')
        genre_model = apps.get_model('movie_store', 'Genre')
        title = input('Enter title: ')
        year = input('Enter year: ')
        director = input('Enter director: ')
        summary = input('Enter summary: ')
        genres = input('Enter genres (comma separated): ')

        try:
            movie = movie_model.objects.create(title=title, year=year, director=director, summary=summary)
            genres = [g.strip() for g in genres.split(',')]
            for g in genres:
                try:
                    genre = genre_model.objects.get(name=g)
                    movie.genres.add(genre)
                except genre_model.DoesNotExist:
                    print('Genre {} does not exist. Skipping...'.format(g))
            print("Movie {} created with id {} and uuid {}".format(movie.title, movie.pk, movie.uuid))
        except Exception as e:
            print('Movie creation failed: {}'.format(e))
