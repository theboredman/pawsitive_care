from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo users for testing role-based login'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing demo users before creating new ones',
        )

    def handle(self, *args, **options):
        if options['delete_existing']:
            self.stdout.write('Deleting existing demo users...')
            User.objects.filter(username__in=['admin', 'vet', 'staff', 'client']).delete()
            self.stdout.write(self.style.SUCCESS('Existing demo users deleted.'))

        demo_users = [
            {
                'username': 'admin',
                'email': 'admin@pawsitivecare.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'phone': '+1-555-0100',
                'address': '123 Admin Street, City, State 12345',
                'role': 'admin',
                'password': 'admin123',
                'is_staff': True,
            },
            {
                'username': 'vet',
                'email': 'vet@pawsitivecare.com',
                'first_name': 'Dr. Sarah',
                'last_name': 'Johnson',
                'phone': '+1-555-0101',
                'address': '456 Veterinary Ave, City, State 12345',
                'role': 'vet',
                'password': 'vet123',
            },
            {
                'username': 'staff',
                'email': 'staff@pawsitivecare.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'phone': '+1-555-0102',
                'address': '789 Staff Lane, City, State 12345',
                'role': 'staff',
                'password': 'staff123',
            },
            {
                'username': 'client',
                'email': 'client@pawsitivecare.com',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'phone': '+1-555-0103',
                'address': '321 Client Road, City, State 12345',
                'role': 'client',
                'password': 'client123',
            }
        ]

        created_count = 0
        for user_data in demo_users:
            try:
                password = user_data.pop('password')
                user = User.objects.create_user(**user_data)
                user.set_password(password)
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created user: {user.username} ({user.get_role_display()})'
                    )
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(f'User {user_data["username"]} already exists.')
                )

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} demo users.')
            )
            self.stdout.write('')
            self.stdout.write('Demo Login Credentials:')
            self.stdout.write('Admin:        username: admin     | password: admin123')
            self.stdout.write('Veterinarian: username: vet       | password: vet123')
            self.stdout.write('Staff:        username: staff     | password: staff123')
            self.stdout.write('Client:       username: client    | password: client123')
        else:
            self.stdout.write('No new users were created.')
