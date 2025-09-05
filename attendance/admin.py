from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'email', 'program', 'level', 'is_active', 'barcode_preview']
    list_filter = ['program', 'level', 'is_active', 'created_at']
    search_fields = ['student_id', 'first_name', 'last_name', 'email', 'barcode_id']
    list_editable = ['is_active']
    readonly_fields = ['barcode_id', 'barcode_image', 'created_at', 'updated_at', 'barcode_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Academic Information', {
            'fields': ('program', 'level')
        }),
        ('Barcode Information', {
            'fields': ('barcode_id', 'barcode_image', 'barcode_preview'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def barcode_preview(self, obj):
        if obj.barcode_image:
            return format_html('<img src="{}" width="100" height="100" />', obj.barcode_image.url)
        return "No barcode"
    barcode_preview.short_description = "Barcode Preview"
    
    actions = ['generate_barcodes', 'activate_students', 'deactivate_students']
    
    def generate_barcodes(self, request, queryset):
        for student in queryset:
            student.generate_barcode()
            student.save()
        self.message_user(request, f"Generated barcodes for {queryset.count()} students.")
    generate_barcodes.short_description = "Generate barcodes for selected students"
    
    def activate_students(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Activated {queryset.count()} students.")
    activate_students.short_description = "Activate selected students"
    
    def deactivate_students(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {queryset.count()} students.")
    deactivate_students.short_description = "Deactivate selected students"


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ['lecturer_id', 'get_full_name', 'get_email', 'department', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['lecturer_id', 'user__first_name', 'user__last_name', 'user__email', 'department']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = "Full Name"
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"


class StudentInline(admin.TabularInline):
    model = Course.students.through
    extra = 0
    verbose_name = "Enrolled Student"
    verbose_name_plural = "Enrolled Students"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'course_name', 'lecturer', 'semester', 'academic_year', 'get_students_count', 'is_active']
    list_filter = ['semester', 'academic_year', 'lecturer__department', 'is_active', 'created_at']
    search_fields = ['course_code', 'course_name', 'description', 'lecturer__lecturer_id']
    list_editable = ['is_active']
    filter_horizontal = ['students']
    readonly_fields = ['created_at', 'updated_at', 'get_students_count']
    inlines = [StudentInline]
    
    fieldsets = (
        ('Course Information', {
            'fields': ('course_code', 'course_name', 'description', 'credit_hours')
        }),
        ('Assignment', {
            'fields': ('lecturer', 'semester', 'academic_year')
        }),
        ('Students', {
            'fields': ('students', 'get_students_count'),
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_students_count(self, obj):
        return obj.students.count()
    get_students_count.short_description = "Enrolled Students"


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    readonly_fields = ['check_in_time', 'scanned_barcode', 'created_at']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id_short', 'course', 'lecturer', 'date', 'start_time', 'status', 'get_attendance_summary']
    list_filter = ['status', 'date', 'course__semester', 'lecturer__department']
    search_fields = ['session_id', 'course__course_code', 'course__course_name', 'session_name']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'get_attendance_summary', 'get_duration']
    inlines = [AttendanceRecordInline]
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'course', 'lecturer', 'session_name', 'location')
        }),
        ('Timing', {
            'fields': ('date', 'start_time', 'end_time', 'get_duration')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Attendance Summary', {
            'fields': ('get_attendance_summary',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def session_id_short(self, obj):
        return obj.session_id[:8] + "..." if len(obj.session_id) > 8 else obj.session_id
    session_id_short.short_description = "Session ID"
    
    def get_attendance_summary(self, obj):
        return f"Present: {obj.present_students}/{obj.total_students} ({obj.attendance_rate:.1f}%)"
    get_attendance_summary.short_description = "Attendance Summary"
    
    def get_duration(self, obj):
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"
    get_duration.short_description = "Duration"
    
    actions = ['end_sessions']
    
    def end_sessions(self, request, queryset):
        active_sessions = queryset.filter(status='active')
        for session in active_sessions:
            session.end_session()
        self.message_user(request, f"Ended {active_sessions.count()} active sessions.")
    end_sessions.short_description = "End selected active sessions"


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['get_session_info', 'student', 'status', 'check_in_time', 'get_late_status', 'created_at']
    list_filter = ['status', 'session__date', 'session__course', 'created_at']
    search_fields = ['student__student_id', 'student__first_name', 'student__last_name', 'session__course__course_code']
    readonly_fields = ['scanned_barcode', 'created_at', 'updated_at', 'get_late_status']
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('session', 'student', 'status', 'check_in_time', 'get_late_status')
        }),
        ('Additional Details', {
            'fields': ('scanned_barcode', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_session_info(self, obj):
        return f"{obj.session.course.course_code} - {obj.session.date}"
    get_session_info.short_description = "Session"
    
    def get_late_status(self, obj):
        return "Yes" if obj.is_late() else "No"
    get_late_status.short_description = "Late?"
    
    actions = ['mark_present', 'mark_absent']
    
    def mark_present(self, request, queryset):
        for record in queryset:
            record.mark_present()
        self.message_user(request, f"Marked {queryset.count()} records as present.")
    mark_present.short_description = "Mark selected records as present"
    
    def mark_absent(self, request, queryset):
        queryset.update(status='absent', check_in_time=None, scanned_barcode='')
        self.message_user(request, f"Marked {queryset.count()} records as absent.")
    mark_absent.short_description = "Mark selected records as absent"


# Customize admin site
admin.site.site_header = "ATU Barcode Attendance System"
admin.site.site_title = "ATU Attendance Admin"
admin.site.index_title = "Welcome to ATU Attendance System Administration"