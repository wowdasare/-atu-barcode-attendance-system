from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import csv
from datetime import datetime, timedelta

from .models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord
from .serializers import (
    LoginSerializer, StudentSerializer, LecturerSerializer, CourseSerializer,
    CourseDetailSerializer, AttendanceSessionSerializer, AttendanceSessionCreateSerializer,
    AttendanceRecordSerializer, BarcodeAttendanceSerializer, AttendanceReportSerializer
)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if user is a lecturer
        try:
            lecturer = user.lecturer
        except Lecturer.DoesNotExist:
            return Response({
                'error': 'Only lecturers can access this system.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'lecturer': {
                'id': lecturer.id,
                'lecturer_id': lecturer.lecturer_id,
                'department': lecturer.department,
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass
    
    return Response({'message': 'Logged out successfully'})


class CourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            lecturer = self.request.user.lecturer
            return Course.objects.filter(lecturer=lecturer, is_active=True)
        except Lecturer.DoesNotExist:
            return Course.objects.none()


class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            lecturer = self.request.user.lecturer
            return Course.objects.filter(lecturer=lecturer, is_active=True)
        except Lecturer.DoesNotExist:
            return Course.objects.none()


class AttendanceSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AttendanceSessionCreateSerializer
        return AttendanceSessionSerializer

    def get_queryset(self):
        try:
            lecturer = self.request.user.lecturer
            return AttendanceSession.objects.filter(lecturer=lecturer).order_by('-start_time')
        except Lecturer.DoesNotExist:
            return AttendanceSession.objects.none()


class AttendanceSessionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AttendanceSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            lecturer = self.request.user.lecturer
            return AttendanceSession.objects.filter(lecturer=lecturer)
        except Lecturer.DoesNotExist:
            return AttendanceSession.objects.none()


@api_view(['POST'])
def start_attendance_session(request):
    serializer = AttendanceSessionCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        session = serializer.save()
        
        # Create attendance records for all students in the course
        students = session.course.students.all()
        for student in students:
            AttendanceRecord.objects.create(
                session=session,
                student=student,
                status='absent'
            )
        
        response_serializer = AttendanceSessionSerializer(session, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def end_attendance_session(request, session_id):
    try:
        lecturer = request.user.lecturer
        session = AttendanceSession.objects.get(session_id=session_id, lecturer=lecturer)
    except (Lecturer.DoesNotExist, AttendanceSession.DoesNotExist):
        return Response({
            'error': 'Session not found or access denied.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if session.status != 'active':
        return Response({
            'error': 'Session is not active.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    session.end_session()
    serializer = AttendanceSessionSerializer(session, context={'request': request})
    
    return Response(serializer.data)


@api_view(['POST'])
def record_attendance(request):
    serializer = BarcodeAttendanceSerializer(data=request.data)
    if serializer.is_valid():
        session = serializer.validated_data['session']
        student = serializer.validated_data['student']
        
        # Get or create attendance record
        attendance_record, created = AttendanceRecord.objects.get_or_create(
            session=session,
            student=student,
            defaults={'status': 'absent'}
        )
        
        # Mark as present
        attendance_record.mark_present(serializer.validated_data['barcode_id'])
        
        # Check if late
        if attendance_record.is_late():
            attendance_record.status = 'late'
            attendance_record.save()
        
        response_serializer = AttendanceRecordSerializer(attendance_record, context={'request': request})
        return Response({
            'message': 'Attendance recorded successfully',
            'attendance': response_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceRecordListView(generics.ListAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        try:
            lecturer = self.request.user.lecturer
            session = AttendanceSession.objects.get(session_id=session_id, lecturer=lecturer)
            # Only return records where students have been scanned (have check_in_time)
            return AttendanceRecord.objects.filter(
                session=session, 
                check_in_time__isnull=False
            ).order_by('student__student_id')
        except (Lecturer.DoesNotExist, AttendanceSession.DoesNotExist):
            return AttendanceRecord.objects.none()


@api_view(['GET'])
def attendance_report(request):
    serializer = AttendanceReportSerializer(data=request.GET)
    if serializer.is_valid():
        course = serializer.validated_data['course']
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        
        # Check if lecturer owns the course
        try:
            lecturer = request.user.lecturer
            if course.lecturer != lecturer:
                return Response({
                    'error': 'Access denied to this course.'
                }, status=status.HTTP_403_FORBIDDEN)
        except Lecturer.DoesNotExist:
            return Response({
                'error': 'Only lecturers can access reports.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Filter sessions
        sessions = AttendanceSession.objects.filter(course=course)
        if start_date:
            sessions = sessions.filter(date__gte=start_date)
        if end_date:
            sessions = sessions.filter(date__lte=end_date)
        
        # Get attendance data
        report_data = []
        for session in sessions.order_by('date'):
            records = AttendanceRecord.objects.filter(session=session)
            session_data = {
                'session_id': session.session_id,
                'date': session.date,
                'session_name': session.session_name,
                'total_students': records.count(),
                'present': records.filter(status='present').count(),
                'late': records.filter(status='late').count(),
                'absent': records.filter(status='absent').count(),
                'attendance_rate': session.attendance_rate,
            }
            report_data.append(session_data)
        
        return Response({
            'course': CourseSerializer(course, context={'request': request}).data,
            'sessions': report_data,
            'summary': {
                'total_sessions': len(report_data),
                'average_attendance': sum(s['attendance_rate'] for s in report_data) / len(report_data) if report_data else 0
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def export_attendance_csv(request):
    serializer = AttendanceReportSerializer(data=request.GET)
    if serializer.is_valid():
        course = serializer.validated_data['course']
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        
        # Check if lecturer owns the course
        try:
            lecturer = request.user.lecturer
            if course.lecturer != lecturer:
                return Response({
                    'error': 'Access denied to this course.'
                }, status=status.HTTP_403_FORBIDDEN)
        except Lecturer.DoesNotExist:
            return Response({
                'error': 'Only lecturers can access reports.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create HTTP response with CSV content
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_{course.course_code}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Student ID', 'Student Name', 'Status', 'Check-in Time'])
        
        # Filter sessions
        sessions = AttendanceSession.objects.filter(course=course)
        if start_date:
            sessions = sessions.filter(date__gte=start_date)
        if end_date:
            sessions = sessions.filter(date__lte=end_date)
        
        # Write attendance data
        for session in sessions.order_by('date'):
            records = AttendanceRecord.objects.filter(session=session).select_related('student')
            for record in records:
                writer.writerow([
                    session.date.strftime('%Y-%m-%d'),
                    record.student.student_id,
                    f"{record.student.first_name} {record.student.last_name}",
                    record.status.title(),
                    record.check_in_time.strftime('%H:%M:%S') if record.check_in_time else '',
                ])
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.request.GET.get('course_id')
        if course_id:
            try:
                lecturer = self.request.user.lecturer
                course = Course.objects.get(id=course_id, lecturer=lecturer)
                return course.students.filter(is_active=True).order_by('student_id')
            except (Lecturer.DoesNotExist, Course.DoesNotExist):
                return Student.objects.none()
        
        return Student.objects.filter(is_active=True).order_by('student_id')