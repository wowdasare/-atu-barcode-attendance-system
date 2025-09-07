"""
URL configuration for atu_barcode_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.auth.models import User
from attendance.models import Lecturer

def setup_users(request):
    """One-time setup view to create users"""
    try:
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
        
        # Create lecturer profile
        lecturer1_profile, created = Lecturer.objects.get_or_create(
            user=lecturer1_user,
            defaults={
                'lecturer_id': 'LEC001',
                'department': 'Computer Science'
            }
        )
        
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
        
        # Create lecturer profile
        lecturer2_profile, created = Lecturer.objects.get_or_create(
            user=lecturer2_user,
            defaults={
                'lecturer_id': 'LEC002',
                'department': 'Information Technology'
            }
        )
        
        return HttpResponse("""
        <h1>✅ Users Created Successfully!</h1>
        <h2>Login Credentials:</h2>
        <ul>
            <li><strong>Admin:</strong> admin / admin123</li>
            <li><strong>Lecturer 1:</strong> kwame_asante / lecturer123</li>
            <li><strong>Lecturer 2:</strong> ama_opoku / lecturer123</li>
        </ul>
        <p><a href="/admin/">Go to Admin Panel</a></p>
        <p><a href="/login/">Go to Web Interface</a></p>
        """)
        
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance.urls')),
    path('setup/', setup_users, name='setup'),  # Temporary setup URL
    path('', include('attendance.web_urls')),
]

# Serve media files in all environments (including production)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
