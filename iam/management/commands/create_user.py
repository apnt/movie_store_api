from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a user in db'

    def handle(self, *args, **options):
        user_model = get_user_model()

        user_email = input('Enter email: ')
        user_first_name = input('Enter first name: ')
        user_last_name = input('Enter last name: ')

        while True:
            password = input('Enter password: ')
            reentered_password = input('Re-enter password: ')
            if password == reentered_password:
                break
            else:
                print("Passwords do not match")

        user = user_model.objects.create_user(
            email=user_email,
            first_name=user_first_name,
            last_name=user_last_name,
            password=password
        )
        print("User {} created with id {} and uuid {}".format(user.email, user.pk, user.uuid))
