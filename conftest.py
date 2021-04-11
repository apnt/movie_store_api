import psycopg2
import pytest
from django.db import connection
from django.conf import settings
from django.core.management import call_command


def django_db_modify_db_settings(schema):
    # Set postgres test schema in django settings
    settings.DATABASES['default']['OPTIONS']['options'] = '-c search_path={test_schema}'.format(test_schema=schema)


def schema_exists(cursor, schema):
    cursor.execute('''SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{test_schema}';'''.
                   format(test_schema=schema))
    return cursor.fetchone() is not None


def drop_db_schema(cursor, schema):
    cursor.execute('''DROP SCHEMA IF EXISTS {test_schema} CASCADE;'''.format(test_schema=schema))


def create_db_schema(cursor, schema):
    cursor.execute('''CREATE SCHEMA IF NOT EXISTS {test_schema};'''.format(test_schema=schema))
    # run migrations, we can add --run-syncdb for faster execution
    call_command('migrate')
    # add initial data
    call_command('loaddata', './common/tests/initial_data.json')


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker, django_db_createdb, django_db_keepdb):
    schema = 'test_movie_store_api'
    django_db_modify_db_settings(schema)
    with django_db_blocker.unblock():
        with connection.cursor() as c:
            # create db only if --create-db arg in pytest.ini or if --reuse-db but test schema does not exist
            create_db = django_db_createdb or (django_db_keepdb and not schema_exists(c, schema))
            if create_db:
                # drop test schema if already exists and create new
                drop_db_schema(c, schema)
                create_db_schema(c, schema)

            # db setup before yield
            yield
            # teardown after yield

            # drop schema after tests run and --reuse-db is not used
            if not django_db_keepdb:
                if c.closed:
                    c = connection.cursor()
                c.execute('''DROP SCHEMA {test_schema} CASCADE;'''.format(test_schema=schema))
                c.close()
