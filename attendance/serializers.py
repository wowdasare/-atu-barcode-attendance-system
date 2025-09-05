from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Must include username and password.')

        return data


class StudentSerializer(serializers.ModelSerializer):
    barcode_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'barcode_id', 'first_name', 'last_name',
            'email', 'phone_number', 'program', 'level', 'barcode_image_url',
            'is_active', 'created_at'
        ]
        read_only_fields = ['barcode_id', 'barcode_image_url', 'created_at']

    def get_barcode_image_url(self, obj):
        if obj.barcode_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.barcode_image.url)
        return None


class LecturerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Lecturer
        fields = [
            'id', 'lecturer_id', 'user', 'full_name', 'department',
            'phone_number', 'is_active', 'created_at'
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer(read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'description', 'lecturer',
            'credit_hours', 'semester', 'academic_year', 'students_count',
            'is_active', 'created_at'
        ]

    def get_students_count(self, obj):
        return obj.students.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer(read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'description', 'lecturer',
            'students', 'credit_hours', 'semester', 'academic_year',
            'is_active', 'created_at'
        ]


class AttendanceSessionSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    lecturer = LecturerSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    attendance_summary = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'session_id', 'course', 'lecturer', 'date', 'start_time',
            'end_time', 'status', 'session_name', 'location', 'notes',
            'duration', 'attendance_summary', 'created_at'
        ]
        read_only_fields = ['session_id']

    def get_duration(self, obj):
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"

    def get_attendance_summary(self, obj):
        return {
            'total_students': obj.total_students,
            'present': obj.present_students,
            'absent': obj.absent_students,
            'attendance_rate': round(obj.attendance_rate, 2)
        }


class AttendanceSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = [
            'course', 'session_name', 'location', 'notes'
        ]

    def create(self, validated_data):
        validated_data['lecturer'] = self.context['request'].user.lecturer
        return super().create(validated_data)


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    session = AttendanceSessionSerializer(read_only=True)
    is_late = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'session', 'student', 'status', 'check_in_time',
            'scanned_barcode', 'notes', 'is_late', 'created_at'
        ]

    def get_is_late(self, obj):
        return obj.is_late()


class BarcodeAttendanceSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    barcode_id = serializers.CharField()

    def validate(self, data):
        session_id = data.get('session_id')
        barcode_id = data.get('barcode_id')

        try:
            session = AttendanceSession.objects.get(session_id=session_id, status='active')
        except AttendanceSession.DoesNotExist:
            raise serializers.ValidationError('Invalid or inactive session.')

        try:
            student = Student.objects.get(barcode_id=barcode_id, is_active=True)
        except Student.DoesNotExist:
            raise serializers.ValidationError('Invalid barcode or inactive student.')

        # Check if student is enrolled in the course
        if not session.course.students.filter(id=student.id).exists():
            raise serializers.ValidationError('Student is not enrolled in this course.')

        data['session'] = session
        data['student'] = student
        return data


class AttendanceReportSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        course_id = data.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
            data['course'] = course
        except Course.DoesNotExist:
            raise serializers.ValidationError('Invalid course ID.')
        
        return data