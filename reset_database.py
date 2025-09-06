#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atu_barcode_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord

def reset_database():
    """
    Reset database but keep admin and lecturer accounts
    """
    print("🗑️  RESETTING DATABASE...")
    print("="*50)
    
    # Count current data
    students_count = Student.objects.count()
    courses_count = Course.objects.count()
    sessions_count = AttendanceSession.objects.count()
    records_count = AttendanceRecord.objects.count()
    users_count = User.objects.count()
    lecturers_count = Lecturer.objects.count()
    
    print(f"📊 CURRENT DATA:")
    print(f"   Users: {users_count}")
    print(f"   Lecturers: {lecturers_count}")
    print(f"   Students: {students_count}")
    print(f"   Courses: {courses_count}")
    print(f"   Sessions: {sessions_count}")
    print(f"   Attendance Records: {records_count}")
    print()
    
    try:
        # 1. Delete all attendance records
        deleted_records = AttendanceRecord.objects.all().delete()
        print(f"✅ Deleted {deleted_records[0]} attendance records")
        
        # 2. Delete all attendance sessions
        deleted_sessions = AttendanceSession.objects.all().delete()
        print(f"✅ Deleted {deleted_sessions[0]} attendance sessions")
        
        # 3. Delete all courses (this will also clear course-student relationships)
        deleted_courses = Course.objects.all().delete()
        print(f"✅ Deleted {deleted_courses[0]} courses")
        
        # 4. Delete all students
        deleted_students = Student.objects.all().delete()
        print(f"✅ Deleted {deleted_students[0]} students")
        
        print()
        print("🎉 DATABASE RESET COMPLETE!")
        print("="*50)
        print("✅ KEPT:")
        print("   - Admin account (admin / admin123)")
        print("   - Lecturer accounts (kwame_asante, ama_opoku)")
        print("   - User authentication system")
        print()
        print("🗑️  CLEARED:")
        print("   - All students")
        print("   - All courses")
        print("   - All attendance sessions")
        print("   - All attendance records")
        print("   - All course enrollments")
        print()
        print("🚀 Ready for fresh client demo!")
        
        # Verify what's left
        remaining_users = User.objects.count()
        remaining_lecturers = Lecturer.objects.count()
        remaining_students = Student.objects.count()
        remaining_courses = Course.objects.count()
        
        print(f"📊 FINAL COUNTS:")
        print(f"   Users: {remaining_users}")
        print(f"   Lecturers: {remaining_lecturers}")
        print(f"   Students: {remaining_students}")
        print(f"   Courses: {remaining_courses}")
        
    except Exception as e:
        print(f"❌ Error during reset: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == '__main__':
    reset_database()