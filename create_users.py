#!/usr/bin/env python
import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atu_barcode_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer

def create_users():
    print("Creating users...")
    
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@atu.edu.gh',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        print(f'✅ Created superuser: admin / admin123')
    else:
        print('ℹ️ Admin user already exists')
    
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
        
        # Create lecturer profile
        lecturer1, created = Lecturer.objects.get_or_create(
            user=user1,
            defaults={
                'lecturer_id': 'LEC001',
                'department': 'Computer Science'
            }
        )
        print(f'✅ Created lecturer: kwame_asante / lecturer123')
    else:
        print('ℹ️ Kwame Asante already exists')
    
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
        
        # Create lecturer profile
        lecturer2, created = Lecturer.objects.get_or_create(
            user=user2,
            defaults={
                'lecturer_id': 'LEC002',
                'department': 'Information Technology'
            }
        )
        print(f'✅ Created lecturer: ama_opoku / lecturer123')
    else:
        print('ℹ️ Ama Opoku already exists')

if __name__ == '__main__':
    create_users()
    print('🎉 User creation completed!')