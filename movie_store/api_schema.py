from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from .serializers import RentalSerializer

# genres
list_genres = {
    'parameters': [
        OpenApiParameter(name='order_by', description='Which field to use when ordering the results.',
                         type=str, enum=['name'])
    ]
}
retrieve_genre = {}
create_genre = {}
partial_update_genre = {}
destroy_genre = {}

# movies
list_movies = {
    'parameters': [
        OpenApiParameter(name='order_by', description='Which field to use when ordering the results.',
                         type=str, enum=['title', 'year']),
        OpenApiParameter(name='year', description='A year to filter the results.', type=int),
        OpenApiParameter(name='director', description='A director to filter the results.', type=str),
        OpenApiParameter(name='genre', type=str,
                         description='Genre to filter the results. Can filter by multiple genres (comma separated). '
                                     'When filtering by multiple genres, only the movies that are associated with all '
                                     'these genres will be listed.', ),
    ]
}
retrieve_movie = {}
create_movie = {}
partial_update_movie = {}
destroy_movie = {}
library = {
    'parameters': [
        OpenApiParameter(name='search', description='A search term.', type=str),
        OpenApiParameter(name='page', description='A page number within the paginated result set.', type=int),
        OpenApiParameter(name='page_size', description='Number of results to return per page.', type=int),
        OpenApiParameter(name='order_by', description='Which field to use when ordering the results.',
                         type=str, enum=['title', 'year']),
        OpenApiParameter(name='year', description='A year to filter the results.', type=int),
        OpenApiParameter(name='director', description='A director to filter the results.', type=str),
        OpenApiParameter(name='genre', type=str,
                         description='Genre to filter the results. Can filter by multiple genres (comma separated). '
                                     'When filtering by multiple genres, only the movies that are associated with all '
                                     'these genres will be listed.', ),
    ]
}

# rentals
list_rentals = {
    'parameters': [
        OpenApiParameter(name='order_by', description='Which field to use when ordering the results.',
                         type=str, enum=['movie__title', 'movie__year', 'rental_date', 'return_date', 'payment']),
        OpenApiParameter(name='user', type=str,
                         description='A user uuid to filter the results. Available only for admins.'),
        OpenApiParameter(name='movie', description='A movie uuid to filter the results.', type=str),
        OpenApiParameter(name='status', type=str, description='A status to filter the results',
                         enum=['active', 'returned']),
    ]
}
retrieve_rental = {
    'examples': [
        OpenApiExample(
            name='Get active rental',
            response_only=True,
            description='Get active rental. The value of "returned" is false, the "return_date" and "payment" are null,'
                        ' and the "fee" field shows the ongoing charge.',
            value={
                'url': 'http://127.0.0.1:9000/store/rentals/fc384551-be65-4292-82f7-ee644a196db5/',
                'user': {
                    'uuid': '5b644978-c908-4f8b-86b2-bf9cfb9f2477',
                    'email': 'user1@test.com',
                    'first_name': 'user',
                    'last_name': '1'
                },
                'movie': {
                    'url': 'http://127.0.0.1:9000/store/movies/966f1207-b163-44b6-9ec2-70df8c983b22/',
                    'genres': [
                        'Action',
                        'Science Fiction'
                    ],
                    'uuid': '966f1207-b163-44b6-9ec2-70df8c983b22',
                    'title': 'Alita: Battle Angel',
                    'year': 2019,
                    'summary': 'When Alita awakens with no memory of who she is in a future world she does not '
                               'recognize, she is taken in by Ido, a compassionate doctor who realizes that '
                               'somewhere in this abandoned cyborg shell is the heart and soul of a young '
                               'woman with an extraordinary past.',
                    'director': 'Robert Rodriguez'
                },
                'uuid': 'fc384551-be65-4292-82f7-ee644a196db5',
                'rental_date': '2021-04-11T21:26:33.022369Z',
                'return_date': None,
                'returned': False,
                'payment': None,
                'fee': 1.0
            }
        ),
        OpenApiExample(
            name='Get returned rental',
            response_only=True,
            description='Get returned rental. The value of "returned" is true, '
                        'and the "return_date" and "payment" are set.',
            value={
                'url': 'http://127.0.0.1:9000/store/rentals/fc384551-be65-4292-82f7-ee644a196db5/',
                'user': {
                    'uuid': '5b644978-c908-4f8b-86b2-bf9cfb9f2477',
                    'email': 'user1@test.com',
                    'first_name': 'user',
                    'last_name': '1'
                },
                'movie': {
                    'url': 'http://127.0.0.1:9000/store/movies/966f1207-b163-44b6-9ec2-70df8c983b22/',
                    'genres': [
                        'Action',
                        'Science Fiction'
                    ],
                    'uuid': '966f1207-b163-44b6-9ec2-70df8c983b22',
                    'title': 'Alita: Battle Angel',
                    'year': 2019,
                    'summary': 'When Alita awakens with no memory of who she is in a future world she does not '
                               'recognize, she is taken in by Ido, a compassionate doctor who realizes that '
                               'somewhere in this abandoned cyborg shell is the heart and soul of a young '
                               'woman with an extraordinary past.',
                    'director': 'Robert Rodriguez'
                },
                'uuid': 'fc384551-be65-4292-82f7-ee644a196db5',
                'rental_date': '2021-04-11T21:26:33.022369Z',
                'return_date': '2021-04-11T21:55:47.883097Z',
                'returned': True,
                'payment': 1.0
            }
        )
    ]
}
create_rental = {
    'responses': {201: RentalSerializer},
    'examples': [OpenApiExample(name='Create rental', request_only=True, description='Create new rental.',
                                value={'movie': '3fa85f64-5717-4562-b3fc-2c963f66afa6'})]
}
partial_update_rental = {'responses': {201: RentalSerializer}, }
destroy_rental = {}
