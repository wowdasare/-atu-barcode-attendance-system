from django.urls import path
from . import web_views

app_name = 'attendance_web'

urlpatterns = [
    # General routes
    path('', web_views.dashboard, name='dashboard'),
    path('login/', web_views.web_login, name='login'),
    path('logout/', web_views.web_logout, name='logout'),
    
    # Lecturer routes
    path('courses/', web_views.course_list, name='course-list'),
    path('courses/<int:course_id>/', web_views.course_detail, name='course-detail'),
    path('sessions/', web_views.session_list, name='session-list'),
    path('sessions/<str:session_id>/', web_views.session_detail, name='session-detail'),
    path('students/', web_views.student_list, name='student-list'),
    
    # Admin routes
    path('admin-dashboard/', web_views.admin_dashboard, name='admin_dashboard'),
    path('admin/lecturers/', web_views.manage_lecturers, name='manage_lecturers'),
    path('admin/lecturers/add/', web_views.add_lecturer, name='add_lecturer'),
    path('admin/students/', web_views.manage_students, name='manage_students'),
    path('admin/students/add/', web_views.add_student, name='add_student'),
    path('admin/courses/', web_views.manage_courses, name='manage_courses'),
]