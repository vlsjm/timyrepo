from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Initialize deployment: create superuser and setup groups'

    def handle(self, *args, **options):
        # Initialize groups and permissions
        self.stdout.write('Setting up groups and permissions...')
        call_command('setup_groups')
        call_command('setup_groups_permissions')
        
        # Get credentials from environment variables
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        # Check if superuser already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" already exists')
            )
        else:
            # Create superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" created successfully'
                )
            )
