#!/usr/bin/env python
"""
One-time script to create users for Railway deployment
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atu_barcode_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Lecturer

# Create admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@atu.edu.gh',
        'first_name': 'System',
        'last_name': 'Administrator',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✅ Created admin user")
else:
    print("ℹ️ Admin user exists")

# Create lecturer 1
lecturer1_user, created = User.objects.get_or_create(
    username='kwame_asante',
    defaults={
        'email': 'kwame.asante@atu.edu.gh',
        'first_name': 'Kwame',
        'last_name': 'Asante',
        'is_staff': True,
        'is_active': True
    }
)
if created:
    lecturer1_user.set_password('lecturer123')
    lecturer1_user.save()
    print("✅ Created lecturer1 user")
else:
    print("ℹ️ Lecturer1 user exists")

# Create lecturer profile
lecturer1_profile, created = Lecturer.objects.get_or_create(
    user=lecturer1_user,
    defaults={
        'lecturer_id': 'LEC001',
        'department': 'Computer Science'
    }
)
if created:
    print("✅ Created lecturer1 profile")

# Create lecturer 2
lecturer2_user, created = User.objects.get_or_create(
    username='ama_opoku',
    defaults={
        'email': 'ama.opoku@atu.edu.gh',
        'first_name': 'Ama',
        'last_name': 'Opoku',
        'is_staff': True,
        'is_active': True
    }
)
if created:
    lecturer2_user.set_password('lecturer123')
    lecturer2_user.save()
    print("✅ Created lecturer2 user")
else:
    print("ℹ️ Lecturer2 user exists")

# Create lecturer profile
lecturer2_profile, created = Lecturer.objects.get_or_create(
    user=lecturer2_user,
    defaults={
        'lecturer_id': 'LEC002',
        'department': 'Information Technology'
    }
)
if created:
    print("✅ Created lecturer2 profile")

print("\n🎉 User setup completed!")
print("Login credentials:")
print("- admin / admin123")
print("- kwame_asante / lecturer123")  
print("- ama_opoku / lecturer123")