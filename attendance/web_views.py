from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord


def web_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                lecturer = user.lecturer
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('attendance_web:dashboard')
            except Lecturer.DoesNotExist:
                messages.error(request, 'Only lecturers can access this system.')
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