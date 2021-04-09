from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a genre in db'

    def handle(self, *args, **options):
        genre_model = apps.get_model('movie_store', 'Genre')
        name = input('Enter genre: ')
        try:
            genre = genre_model.objects.create(name=name)
            print("Genre {} created with id {} and uuid {}".format(genre.name, genre.pk, genre.uuid))
        except Exception as e:
            print('Genre creation failed: {}'.format(e))
