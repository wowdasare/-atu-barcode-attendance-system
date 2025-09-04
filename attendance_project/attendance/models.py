from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    barcode_id = models.CharField(max_length=50, unique=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)
    program = models.CharField(max_length=100)
    level = models.CharField(max_length=10)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.barcode_id:
            self.barcode_id = str(uuid.uuid4())
        
        # Only generate barcode if we don't have one and we're not loading fixtures
        generate_barcode = not self.barcode_image and not kwargs.get('skip_barcode', False)
        
        super().save(*args, **kwargs)
        
        if generate_barcode:
            self.generate_barcode()
            super().save(update_fields=['barcode_image'])

    def generate_barcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.barcode_id)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        filename = f'barcode_{self.student_id}.png'
        filebuffer = File(buffer, name=filename)
        self.barcode_image.save(filename, filebuffer)


class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lecturer_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['lecturer_id']

    def __str__(self):
        return f"{self.lecturer_id} - {self.user.first_name} {self.user.last_name}"


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='courses')
    students = models.ManyToManyField(Student, related_name='courses', blank=True)
    credit_hours = models.IntegerField(default=3)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course_code']
        unique_together = ['course_code', 'semester', 'academic_year']

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class AttendanceSession(models.Model):
    SESSION_STATUS = [
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    session_id = models.CharField(max_length=50, unique=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='attendance_sessions')
    date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=SESSION_STATUS, default='active')
    session_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.course.course_code} - {self.date} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def end_session(self):
        self.status = 'ended'
        self.end_time = timezone.now()
        self.save()

    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time

    @property
    def total_students(self):
        return self.course.students.count()

    @property
    def present_students(self):
        return self.attendance_records.filter(status='present').count()

    @property
    def absent_students(self):
        return self.total_students - self.present_students

    @property
    def attendance_rate(self):
        if self.total_students == 0:
            return 0
        return (self.present_students / self.total_students) * 100


class AttendanceRecord(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='absent')
    check_in_time = models.DateTimeField(null=True, blank=True)
    scanned_barcode = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session', 'student']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.session.course.course_code} ({self.status})"

    def mark_present(self, barcode_id=None):
        self.status = 'present'
        self.check_in_time = timezone.now()
        if barcode_id:
            self.scanned_barcode = barcode_id
        self.save()

    def is_late(self):
        if self.check_in_time and self.session.start_time:
            grace_period = timezone.timedelta(minutes=15)  # 15 minutes grace period
            return self.check_in_time > (self.session.start_time + grace_period)
        return False