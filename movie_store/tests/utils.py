import random
from movie_store.models import Movie


def get_random_movies(number_of_movies):
    """Gets some random movies from the database"""
    movies_in_db = Movie.objects.all()
    return random.sample(list(movies_in_db), number_of_movies)