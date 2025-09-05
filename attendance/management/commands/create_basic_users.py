from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Lecturer


class Command(BaseCommand):
    help = 'Create basic users for the attendance system'

    def handle(self, *args, **options):
        self.stdout.write('Creating basic users...')
        
        try:
            # Create superuser
            if not User.objects.filter(username='admin').exists():
                admin = User.objects.create_superuser(
                    username='admin',
                    email='admin@atu.edu.gh',
                    password='admin123',
                    first_name='System',
                    last_name='Administrator'
                )
                self.stdout.write(self.style.SUCCESS('✅ Created superuser: admin / admin123'))
            else:
                self.stdout.write('ℹ️ Admin user already exists')
            
            # Create lecturer 1
            if not User.objects.filter(username='kwame_asante').exists():
                user1 = User.objects.create_user(
                    username='kwame_asante',
                    email='kwame.asante@atu.edu.gh',
                    password='lecturer123',
                    first_name='Kwame',
                    last_name='Asante',
                    is_staff=True,
                    is_active=True
                )
                
                # Create lecturer profile if it doesn't exist
                lecturer1, created = Lecturer.objects.get_or_create(
                    user=user1,
                    defaults={
                        'lecturer_id': 'LEC001',
                        'department': 'Computer Science'
                    }
                )
                self.stdout.write(self.style.SUCCESS('✅ Created lecturer: kwame_asante / lecturer123'))
            else:
                self.stdout.write('ℹ️ Kwame Asante already exists')
            
            # Create lecturer 2
            if not User.objects.filter(username='ama_opoku').exists():
                user2 = User.objects.create_user(
                    username='ama_opoku',
                    email='ama.opoku@atu.edu.gh',
                    password='lecturer123',
                    first_name='Ama',
                    last_name='Opoku',
                    is_staff=True,
                    is_active=True
                )
                
                # Create lecturer profile if it doesn't exist
                lecturer2, created = Lecturer.objects.get_or_create(
                    user=user2,
                    defaults={
                        'lecturer_id': 'LEC002',
                        'department': 'Information Technology'
                    }
                )
                self.stdout.write(self.style.SUCCESS('✅ Created lecturer: ama_opoku / lecturer123'))
            else:
                self.stdout.write('ℹ️ Ama Opoku already exists')
                
            self.stdout.write(self.style.SUCCESS('🎉 Basic user creation completed!'))
            self.stdout.write('')
            self.stdout.write('Login credentials:')
            self.stdout.write('- Admin: admin / admin123')
            self.stdout.write('- Lecturer 1: kwame_asante / lecturer123')
            self.stdout.write('- Lecturer 2: ama_opoku / lecturer123')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating users: {str(e)}'))
            raise e