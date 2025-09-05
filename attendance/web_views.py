from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from django.utils import timezone
import csv

from .models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord


def web_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Check user role and redirect accordingly
            if user.is_superuser:
                messages.success(request, f'Welcome back, {user.first_name}! (Administrator)')
                return redirect('attendance_web:admin_dashboard')
            else:
                try:
                    lecturer = user.lecturer
                    messages.success(request, f'Welcome back, {user.first_name}! (Lecturer)')
                    return redirect('attendance_web:dashboard')
                except Lecturer.DoesNotExist:
                    messages.error(request, 'Access denied. User account not properly configured.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'attendance/login.html')


def web_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('attendance_web:login')


@login_required
def dashboard(request):
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'Access denied. Lecturer profile not found.')
        return redirect('attendance_web:login')
    
    # Get statistics
    total_courses = Course.objects.filter(lecturer=lecturer, is_active=True).count()
    active_sessions = AttendanceSession.objects.filter(lecturer=lecturer, status='active').count()
    
    # Recent sessions
    recent_sessions = AttendanceSession.objects.filter(
        lecturer=lecturer
    ).order_by('-start_time')[:5]
    
    # Course statistics
    courses = Course.objects.filter(lecturer=lecturer, is_active=True).annotate(
        total_students=Count('students')
    )
    
    context = {
        'lecturer': lecturer,
        'total_courses': total_courses,
        'active_sessions': active_sessions,
        'recent_sessions': recent_sessions,
        'courses': courses,
    }
    
    return render(request, 'attendance/dashboard.html', context)


@login_required
def course_list(request):
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'Access denied. Lecturer profile not found.')
        return redirect('attendance_web:login')
    
    courses = Course.objects.filter(lecturer=lecturer, is_active=True).annotate(
        total_students=Count('students'),
        total_sessions=Count('attendance_sessions')
    ).order_by('course_code')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(course_code__icontains=search_query) |
            Q(course_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
        'search_query': search_query,
    }
    
    return render(request, 'attendance/course_list.html', context)


@login_required
def course_detail(request, course_id):
    try:
        lecturer = request.user.lecturer
        course = get_object_or_404(Course, id=course_id, lecturer=lecturer, is_active=True)
    except Lecturer.DoesNotExist:
        messages.error(request, 'Access denied. Lecturer profile not found.')
        return redirect('attendance_web:login')
    
    # Get sessions for this course
    sessions = AttendanceSession.objects.filter(course=course).order_by('-start_time')
    
    # Get course statistics
    total_sessions = sessions.count()
    active_sessions = sessions.filter(status='active').count()
    
    # Average attendance rate
    completed_sessions = sessions.filter(status='ended')
    if completed_sessions.exists():
        avg_attendance = sum(session.attendance_rate for session in completed_sessions) / completed_sessions.count()
    else:
        avg_attendance = 0
    
    context = {
        'course': course,
        'sessions': sessions[:10],  # Show only last 10 sessions
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'avg_attendance': avg_attendance,
    }
    
    return render(request, 'attendance/course_detail.html', context)


@login_required
def session_list(request):
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'Access denied. Lecturer profile not found.')
        return redirect('attendance_web:login')
    
    sessions = AttendanceSession.objects.filter(lecturer=lecturer).order_by('-start_time')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    # Filter by course
    course_filter = request.GET.get('course')
    if course_filter:
        sessions = sessions.filter(course_id=course_filter)
    
    # Pagination
    paginator = Paginator(sessions, 15)
    page_number = request.GET.get('page')
    sessions = paginator.get_page(page_number)
    
    # Get courses for filter
    courses = Course.objects.filter(lecturer=lecturer, is_active=True).order_by('course_code')
    
    context = {
        'sessions': sessions,
        'courses': courses,
        'status_filter': status_filter,
        'course_filter': course_filter,
    }
    
    return render(request, 'attendance/session_list.html', context)


@login_required
def session_detail(request, session_id):
    try:
        lecturer = request.user.lecturer
        session = get_object_or_404(AttendanceSession, session_id=session_id, lecturer=lecturer)
    except Lecturer.DoesNotExist:
        messages.error(request, 'Access denied. Lecturer profile not found.')
        return redirect('attendance_web:login')
    
    # Get attendance records
    records = AttendanceRecord.objects.filter(session=session).select_related('student').order_by('student__student_id')
    
    # Statistics
    total_students = records.count()
    present_count = records.filter(status='present').count()
    late_count = records.filter(status='late').count()
    absent_count = records.filter(status='absent').count()
    
    context = {
        'session': session,
        'records': records,
        'total_students': total_students,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
    }
    
    return render(request, 'attendance/session_detail.html', context)


@login_required
def student_list(request):
    try:
        lecturer = request.user.lecturer
    except Lecturer.DoesNotExist:
        messages.error(request, 'Access denied. Lecturer profile not found.')
        return redirect('attendance_web:login')
    
    # Get all students from lecturer's courses
    course_ids = Course.objects.filter(lecturer=lecturer, is_active=True).values_list('id', flat=True)
    students = Student.objects.filter(courses__in=course_ids, is_active=True).distinct().order_by('student_id')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    
    return render(request, 'attendance/student_list.html', context)


# Helper function to check if user is admin
def is_admin(user):
    print(f"[DEBUG] is_admin check for user: {user.username}, is_superuser: {user.is_superuser}")
    return user.is_superuser


# Diagnostic view to check admin access
@login_required
def admin_debug(request):
    """Debug view to check admin access"""
    debug_info = {
        'user': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_admin_result': is_admin(request.user),
    }
    
    return render(request, 'attendance/admin_debug.html', {'debug_info': debug_info})


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Debug: Log that this view is being accessed
    print(f"[DEBUG] Admin dashboard accessed by user: {request.user.username}")
    
    # Get system statistics
    total_users = User.objects.count()
    total_lecturers = Lecturer.objects.count()
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    active_sessions = AttendanceSession.objects.filter(status='active').count()
    
    # Recent activities
    recent_sessions = AttendanceSession.objects.all().order_by('-start_time')[:5]
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_lecturers': total_lecturers,
        'total_students': total_students,
        'total_courses': total_courses,
        'active_sessions': active_sessions,
        'recent_sessions': recent_sessions,
        'recent_users': recent_users,
    }
    
    return render(request, 'attendance/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manage_lecturers(request):
    print(f"[DEBUG] Manage lecturers accessed by user: {request.user.username}")
    lecturers = Lecturer.objects.select_related('user').order_by('lecturer_id')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        lecturers = lecturers.filter(
            Q(lecturer_id__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(lecturers, 15)
    page_number = request.GET.get('page')
    lecturers = paginator.get_page(page_number)
    
    context = {
        'lecturers': lecturers,
        'search_query': search_query,
    }
    
    return render(request, 'attendance/manage_lecturers.html', context)


@login_required
@user_passes_test(is_admin)
def add_lecturer(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        lecturer_id = request.POST.get('lecturer_id')
        department = request.POST.get('department')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_staff=True,
                is_active=True
            )
            
            # Create lecturer profile
            Lecturer.objects.create(
                user=user,
                lecturer_id=lecturer_id,
                department=department
            )
            
            messages.success(request, f'Lecturer {first_name} {last_name} created successfully!')
            return redirect('attendance_web:manage_lecturers')
            
        except Exception as e:
            messages.error(request, f'Error creating lecturer: {str(e)}')
    
    return render(request, 'attendance/add_lecturer.html')


@login_required
@user_passes_test(is_admin)
def manage_students(request):
    students = Student.objects.filter(is_active=True).order_by('student_id')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(program__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    
    return render(request, 'attendance/manage_students.html', context)


@login_required
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        # Get form data
        student_id = request.POST.get('student_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        program = request.POST.get('program')
        level = request.POST.get('level')
        
        try:
            # Create student
            student = Student.objects.create(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                program=program,
                level=level,
                is_active=True
            )
            
            messages.success(request, f'Student {first_name} {last_name} created successfully!')
            return redirect('attendance_web:manage_students')
            
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}')
    
    return render(request, 'attendance/add_student.html')


@login_required
@user_passes_test(is_admin)
def manage_courses(request):
    courses = Course.objects.filter(is_active=True).select_related('lecturer').order_by('course_code')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            Q(course_code__icontains=search_query) |
            Q(course_name__icontains=search_query) |
            Q(lecturer__user__first_name__icontains=search_query) |
            Q(lecturer__user__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(courses, 15)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
        'search_query': search_query,
    }
    
    return render(request, 'attendance/manage_courses.html', context)


@login_required
@user_passes_test(is_admin)
def add_course(request):
    if request.method == 'POST':
        # Get form data
        course_code = request.POST.get('course_code')
        course_name = request.POST.get('course_name')
        description = request.POST.get('description')
        lecturer_id = request.POST.get('lecturer_id')
        credit_hours = request.POST.get('credit_hours')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        
        try:
            # Get lecturer
            lecturer = Lecturer.objects.get(id=lecturer_id)
            
            # Create course
            course = Course.objects.create(
                course_code=course_code,
                course_name=course_name,
                description=description,
                lecturer=lecturer,
                credit_hours=int(credit_hours),
                semester=semester,
                academic_year=academic_year,
                is_active=True
            )
            
            messages.success(request, f'Course {course_code} - {course_name} created successfully!')
            return redirect('attendance_web:manage_courses')
            
        except Exception as e:
            messages.error(request, f'Error creating course: {str(e)}')
    
    # Get all lecturers for the dropdown
    lecturers = Lecturer.objects.filter(user__is_active=True).select_related('user')
    
    context = {
        'lecturers': lecturers,
    }
    
    return render(request, 'attendance/add_course.html', context)


# CSV Export Functions
@login_required
@user_passes_test(is_admin)
def export_students_csv(request):
    """Export all students to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Program', 'Level', 'Status', 'Created Date'])
    
    students = Student.objects.filter(is_active=True).order_by('student_id')
    for student in students:
        writer.writerow([
            student.student_id,
            student.first_name,
            student.last_name,
            student.email,
            student.program,
            student.level,
            'Active' if student.is_active else 'Inactive',
            student.created_at.strftime('%Y-%m-%d')
        ])
    
    return response


@login_required
@user_passes_test(is_admin)
def export_lecturers_csv(request):
    """Export all lecturers to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lecturers_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Lecturer ID', 'First Name', 'Last Name', 'Email', 'Username', 'Department', 'Status', 'Created Date'])
    
    lecturers = Lecturer.objects.select_related('user').order_by('lecturer_id')
    for lecturer in lecturers:
        writer.writerow([
            lecturer.lecturer_id,
            lecturer.user.first_name,
            lecturer.user.last_name,
            lecturer.user.email,
            lecturer.user.username,
            lecturer.department,
            'Active' if lecturer.user.is_active else 'Inactive',
            lecturer.created_at.strftime('%Y-%m-%d')
        ])
    
    return response


@login_required
@user_passes_test(is_admin)
def export_courses_csv(request):
    """Export all courses to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="courses_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Course Code', 'Course Name', 'Lecturer', 'Department', 'Credit Hours', 'Semester', 'Academic Year', 'Total Students', 'Status'])
    
    courses = Course.objects.filter(is_active=True).select_related('lecturer').order_by('course_code')
    for course in courses:
        writer.writerow([
            course.course_code,
            course.course_name,
            f"{course.lecturer.user.first_name} {course.lecturer.user.last_name}",
            course.lecturer.department,
            course.credit_hours,
            course.semester,
            course.academic_year,
            course.students.count(),
            'Active' if course.is_active else 'Inactive'
        ])
    
    return response


@login_required
def export_attendance_csv(request, course_id=None):
    """Export attendance records to CSV"""
    # Allow both admin and lecturers to export attendance
    if not (request.user.is_superuser or hasattr(request.user, 'lecturer')):
        messages.error(request, 'Access denied.')
        return redirect('attendance_web:login')
    
    response = HttpResponse(content_type='text/csv')
    
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            # Check if lecturer owns the course (unless admin)
            if not request.user.is_superuser and hasattr(request.user, 'lecturer'):
                if course.lecturer != request.user.lecturer:
                    messages.error(request, 'Access denied to this course.')
                    return redirect('attendance_web:dashboard')
            
            filename = f"attendance_{course.course_code}.csv"
            sessions = AttendanceSession.objects.filter(course=course)
        except Course.DoesNotExist:
            messages.error(request, 'Course not found.')
            return redirect('attendance_web:dashboard')
    else:
        # Export all attendance (admin only)
        if not request.user.is_superuser:
            messages.error(request, 'Access denied.')
            return redirect('attendance_web:dashboard')
        filename = "attendance_all_courses.csv"
        sessions = AttendanceSession.objects.all()
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Course Code', 'Course Name', 'Session Name', 'Student ID', 'Student Name', 'Status', 'Check-in Time', 'Lecturer'])
    
    for session in sessions.select_related('course', 'lecturer').order_by('-date'):
        records = AttendanceRecord.objects.filter(session=session).select_related('student')
        for record in records:
            writer.writerow([
                session.date.strftime('%Y-%m-%d'),
                session.course.course_code,
                session.course.course_name,
                session.session_name or f"Session {session.date}",
                record.student.student_id,
                f"{record.student.first_name} {record.student.last_name}",
                record.status.title(),
                record.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.check_in_time else '',
                f"{session.lecturer.user.first_name} {session.lecturer.user.last_name}"
            ])
    
    return response