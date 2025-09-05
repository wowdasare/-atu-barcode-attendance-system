from django.urls import path
from . import views

app_name = 'attendance_api'

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Courses
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    
    # Attendance Sessions
    path('sessions/', views.AttendanceSessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<int:pk>/', views.AttendanceSessionDetailView.as_view(), name='session-detail'),
    path('sessions/start/', views.start_attendance_session, name='start-session'),
    path('sessions/<str:session_id>/end/', views.end_attendance_session, name='end-session'),
    
    # Attendance Recording
    path('attendance/record/', views.record_attendance, name='record-attendance'),
    path('attendance/session/<str:session_id>/', views.AttendanceRecordListView.as_view(), name='session-attendance'),
    
    # Reports and Export
    path('reports/attendance/', views.attendance_report, name='attendance-report'),
    path('reports/export/csv/', views.export_attendance_csv, name='export-csv'),
    
    # Students
    path('students/', views.StudentListView.as_view(), name='student-list'),
]