from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a user in db'

    def handle(self, *args, **options):
        user_model = get_user_model()

        email = input('Enter email: ')
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')

        while True:
            password = input('Enter password: ')
            reentered_password = input('Re-enter password: ')
            if password == reentered_password:
                break
            else:
                print("Passwords do not match")

        try:
            user = user_model.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            print("User {} created with id {} and uuid {}".format(user.email, user.pk, user.uuid))
        except Exception as e:
            print('User creation failed: {}'.format(e))
