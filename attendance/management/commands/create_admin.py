from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create admin superuser only - no sample data'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@atu.edu.gh')
        parser.add_argument('--password', type=str, default='admin123')
        parser.add_argument('--noinput', action='store_true', help='Do not prompt for input')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists.')
            )
            return
        
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user "{username}"')
        )
        self.stdout.write(f'Login: {username} / {password}')