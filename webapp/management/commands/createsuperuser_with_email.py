from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.contrib.auth import get_user_model

class Command(createsuperuser.Command):
    help = 'Create a superuser with an email address instead of a username'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--custom-email', type=str, required=True, help='Email address for the superuser')
        parser.add_argument('--custom-password', type=str, required=True, help='Password for the superuser')

    def handle(self, *args, **options):
        email = options.get('custom_email')
        password = options.get('custom_password')

        if not email:
            raise CommandError('You must provide an email address')

        if not password:
            raise CommandError('You must provide a password')

        UserModel = get_user_model()
        user_data = {
            'email': email,
            'password': password,
            'is_staff': True,
            'is_superuser': True,
        }

        user = UserModel._default_manager.db_manager('default').create_user(**user_data)
        self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))