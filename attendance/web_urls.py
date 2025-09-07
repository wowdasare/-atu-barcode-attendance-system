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
    
    # Debug route
    path('system/debug/', web_views.admin_debug, name='admin_debug'),
    
    # Admin routes (changed prefix to avoid Django admin conflict)
    path('admin-dashboard/', web_views.admin_dashboard, name='admin_dashboard'),
    path('system/lecturers/', web_views.manage_lecturers, name='manage_lecturers'),
    path('system/lecturers/add/', web_views.add_lecturer, name='add_lecturer'),
    path('system/students/', web_views.manage_students, name='manage_students'),
    path('system/students/add/', web_views.add_student, name='add_student'),
    path('system/courses/', web_views.manage_courses, name='manage_courses'),
    path('system/courses/add/', web_views.add_course, name='add_course'),
    
    # CSV Export routes
    path('export/students/', web_views.export_students_csv, name='export_students'),
    path('export/lecturers/', web_views.export_lecturers_csv, name='export_lecturers'),
    path('export/courses/', web_views.export_courses_csv, name='export_courses'),
    path('export/attendance/', web_views.export_attendance_csv, name='export_attendance'),
    path('export/attendance/<int:course_id>/', web_views.export_attendance_csv, name='export_course_attendance'),
    
    # Edit/Action routes
    path('system/students/<int:student_id>/edit/', web_views.edit_student, name='edit_student'),
    path('system/lecturers/<int:lecturer_id>/edit/', web_views.edit_lecturer, name='edit_lecturer'),
    path('system/courses/<int:course_id>/students/', web_views.manage_course_students, name='manage_course_students'),
    path('system/students/<int:student_id>/toggle/', web_views.toggle_student_status, name='toggle_student_status'),
    path('system/lecturers/<int:lecturer_id>/toggle/', web_views.toggle_lecturer_status, name='toggle_lecturer_status'),
    path('system/students/<int:student_id>/barcode/', web_views.generate_student_barcode, name='generate_barcode'),
    path('system/students/<int:student_id>/show-barcode/', web_views.show_barcode, name='show_barcode'),
    path('barcode/<int:student_id>.png', web_views.serve_barcode_image, name='serve_barcode'),
]