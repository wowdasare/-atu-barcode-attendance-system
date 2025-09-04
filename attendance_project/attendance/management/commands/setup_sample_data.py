from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import Student, Lecturer, Course, AttendanceSession, AttendanceRecord
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Set up sample data for testing the attendance system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up sample data...')
        
        # Load fixtures first
        self.stdout.write('Loading sample data fixtures...')
        
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@atu.edu.gh',
                password='admin123',
                first_name='System',
                last_name='Administrator'
            )
            self.stdout.write(f'Created superuser: admin (password: admin123)')
        
        # Create lecturer users and set passwords
        lecturer_users = [
            {
                'username': 'kwame_asante',
                'email': 'kwame.asante@atu.edu.gh',
                'first_name': 'Kwame',
                'last_name': 'Asante',
                'password': 'lecturer123'
            },
            {
                'username': 'ama_opoku',
                'email': 'ama.opoku@atu.edu.gh',
                'first_name': 'Ama',
                'last_name': 'Opoku',
                'password': 'lecturer123'
            }
        ]
        
        for lecturer_data in lecturer_users:
            user, created = User.objects.get_or_create(
                username=lecturer_data['username'],
                defaults={
                    'email': lecturer_data['email'],
                    'first_name': lecturer_data['first_name'],
                    'last_name': lecturer_data['last_name'],
                    'is_staff': True,
                    'is_active': True
                }
            )
            if created:
                user.set_password(lecturer_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.username}')
        
        # Create lecturers
        lecturers_data = [
            {
                'user': User.objects.get(username='kwame_asante'),
                'lecturer_id': 'LEC001',
                'department': 'Computer Science',
                'phone_number': '+233244123456'
            },
            {
                'user': User.objects.get(username='ama_opoku'),
                'lecturer_id': 'LEC002',
                'department': 'Information Technology',
                'phone_number': '+233244654321'
            }
        ]
        
        for lecturer_data in lecturers_data:
            lecturer, created = Lecturer.objects.get_or_create(
                lecturer_id=lecturer_data['lecturer_id'],
                defaults=lecturer_data
            )
            if created:
                self.stdout.write(f'Created lecturer: {lecturer.lecturer_id}')
        
        # Create students
        students_data = [
            {
                'student_id': 'ATU2024001',
                'first_name': 'John',
                'last_name': 'Mensah',
                'email': 'john.mensah@student.atu.edu.gh',
                'phone_number': '+233244111111',
                'program': 'HND Computer Science',
                'level': 'Level 3'
            },
            {
                'student_id': 'ATU2024002',
                'first_name': 'Mary',
                'last_name': 'Adjei',
                'email': 'mary.adjei@student.atu.edu.gh',
                'phone_number': '+233244222222',
                'program': 'HND Computer Science',
                'level': 'Level 3'
            },
            {
                'student_id': 'ATU2024003',
                'first_name': 'Peter',
                'last_name': 'Osei',
                'email': 'peter.osei@student.atu.edu.gh',
                'phone_number': '+233244333333',
                'program': 'HND Information Technology',
                'level': 'Level 3'
            },
            {
                'student_id': 'ATU2024004',
                'first_name': 'Grace',
                'last_name': 'Boateng',
                'email': 'grace.boateng@student.atu.edu.gh',
                'phone_number': '+233244444444',
                'program': 'HND Information Technology',
                'level': 'Level 3'
            },
            {
                'student_id': 'ATU2024005',
                'first_name': 'Samuel',
                'last_name': 'Appiah',
                'email': 'samuel.appiah@student.atu.edu.gh',
                'phone_number': '+233244555555',
                'program': 'HND Computer Science',
                'level': 'Level 2'
            }
        ]
        
        for student_data in students_data:
            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults=student_data
            )
            if created:
                self.stdout.write(f'Created student: {student.student_id} - {student.first_name} {student.last_name}')
        
        # Create courses
        courses_data = [
            {
                'course_code': 'CS301',
                'course_name': 'Database Systems',
                'description': 'Introduction to database design, SQL, and database management systems.',
                'lecturer': Lecturer.objects.get(lecturer_id='LEC001'),
                'credit_hours': 3,
                'semester': 'Semester 1',
                'academic_year': '2024/2025'
            },
            {
                'course_code': 'CS302',
                'course_name': 'Web Development',
                'description': 'Modern web development using HTML, CSS, JavaScript, and frameworks.',
                'lecturer': Lecturer.objects.get(lecturer_id='LEC001'),
                'credit_hours': 3,
                'semester': 'Semester 1',
                'academic_year': '2024/2025'
            },
            {
                'course_code': 'IT301',
                'course_name': 'Network Administration',
                'description': 'Network setup, configuration, and administration principles.',
                'lecturer': Lecturer.objects.get(lecturer_id='LEC002'),
                'credit_hours': 3,
                'semester': 'Semester 1',
                'academic_year': '2024/2025'
            }
        ]
        
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                course_code=course_data['course_code'],
                defaults=course_data
            )
            if created:
                self.stdout.write(f'Created course: {course.course_code} - {course.course_name}')
        
        # Enroll students in courses
        cs_students = Student.objects.filter(program__icontains='Computer Science')
        it_students = Student.objects.filter(program__icontains='Information Technology')
        
        # Enroll CS students in CS courses
        cs301 = Course.objects.get(course_code='CS301')
        cs302 = Course.objects.get(course_code='CS302')
        
        for student in cs_students:
            cs301.students.add(student)
            cs302.students.add(student)
        
        # Enroll IT students in IT course
        it301 = Course.objects.get(course_code='IT301')
        for student in it_students:
            it301.students.add(student)
        
        # Create some sample attendance sessions
        now = timezone.now()
        
        # Create a recent session for CS301
        session1 = AttendanceSession.objects.create(
            course=cs301,
            lecturer=cs301.lecturer,
            date=now.date(),
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            status='ended',
            session_name='Database Design Lecture',
            location='Lab A'
        )
        
        # Create attendance records for this session
        students = cs301.students.all()
        for i, student in enumerate(students):
            status = 'present' if i < 3 else 'absent'
            check_in_time = session1.start_time + timedelta(minutes=5) if status == 'present' else None
            
            AttendanceRecord.objects.create(
                session=session1,
                student=student,
                status=status,
                check_in_time=check_in_time,
                scanned_barcode=student.barcode_id if status == 'present' else ''
            )
        
        self.stdout.write(
            self.style.SUCCESS('Sample data setup completed successfully!')
        )
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('- Admin: admin / admin123')
        self.stdout.write('- Lecturer 1: kwame_asante / lecturer123')
        self.stdout.write('- Lecturer 2: ama_opoku / lecturer123')