# ATU Barcode Attendance System

A comprehensive Django backend for barcode-based attendance tracking system for Accra Technical University (ATU). This system allows lecturers to manage attendance sessions and students to check in using unique barcode/QR codes.

## Features

### Core Functionality
- **Student Management**: Unique barcode generation for each student
- **Lecturer Authentication**: Secure login system for lecturers
- **Course Management**: Create and manage courses with student enrollment
- **Attendance Sessions**: Start/end attendance sessions for specific courses
- **Barcode Scanning**: Record attendance via barcode/QR code scanning
- **Real-time Tracking**: Monitor attendance status in real-time

### Administrative Features
- **Admin Interface**: Comprehensive Django admin for system management
- **Web Dashboard**: Lecturer dashboard for managing courses and sessions
- **Attendance Reports**: Generate detailed attendance reports
- **CSV Export**: Export attendance data to CSV format
- **Student Analytics**: Track individual and course-wide attendance patterns

### API Features
- **REST API**: Full REST API for mobile app integration
- **CORS Support**: Configured for cross-origin requests
- **Token Authentication**: Secure API authentication for mobile apps
- **JSON Responses**: Structured JSON responses for all endpoints

## Technology Stack

- **Backend**: Django 5.2+ with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in authentication + Token auth
- **Barcode Generation**: QR codes with qrcode library
- **CORS**: django-cors-headers for mobile app integration
- **Image Processing**: Pillow for barcode image handling

## Project Structure

```
attendance_project/
├── attendance_project/          # Main project settings
│   ├── settings.py             # Django settings with CORS, REST framework
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py/asgi.py        # WSGI/ASGI configuration
├── attendance/                 # Main attendance app
│   ├── models.py              # Data models (Student, Lecturer, Course, etc.)
│   ├── views.py               # API views and business logic
│   ├── serializers.py         # REST API serializers
│   ├── admin.py               # Django admin configuration
│   ├── web_views.py           # Web interface views
│   ├── urls.py                # API URL patterns
│   ├── web_urls.py            # Web interface URL patterns
│   └── management/commands/   # Custom management commands
├── templates/                  # HTML templates for web interface
├── static/                    # Static files (CSS, JS, images)
├── media/                     # User uploaded files (barcode images)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation & Setup

### 1. Clone and Navigate
```bash
cd attendance_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py migrate
```

### 5. Load Sample Data (Optional)
```bash
python manage.py setup_sample_data
```

### 6. Run Development Server
```bash
python manage.py runserver
```

## Default Login Credentials

After running `setup_sample_data`:

- **Admin Panel**: admin / admin123
- **Lecturer 1**: kwame_asante / lecturer123
- **Lecturer 2**: ama_opoku / lecturer123

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Lecturer login
- `POST /api/auth/logout/` - Logout

### Courses
- `GET /api/courses/` - List lecturer's courses
- `GET /api/courses/{id}/` - Course details with enrolled students

### Attendance Sessions
- `GET /api/sessions/` - List attendance sessions
- `POST /api/sessions/start/` - Start new attendance session
- `POST /api/sessions/{session_id}/end/` - End attendance session
- `GET /api/sessions/{id}/` - Session details

### Attendance Recording
- `POST /api/attendance/record/` - Record attendance via barcode scan
- `GET /api/attendance/session/{session_id}/` - Get session attendance records

### Reports & Export
- `GET /api/reports/attendance/` - Generate attendance report
- `GET /api/reports/export/csv/` - Export attendance to CSV

### Students
- `GET /api/students/` - List students (with course filter)

## Web Interface

### Lecturer Dashboard
- Access: `http://localhost:8000/`
- Features: Course overview, session management, attendance statistics

### Admin Interface
- Access: `http://localhost:8000/admin/`
- Features: Complete system administration

## Database Models

### Core Models
1. **Student**: Student information with unique barcode ID
2. **Lecturer**: Lecturer profile linked to Django User
3. **Course**: Course information with lecturer assignment
4. **AttendanceSession**: Individual attendance sessions
5. **AttendanceRecord**: Individual student attendance records

### Key Relationships
- Lecturer → Courses (One to Many)
- Course → Students (Many to Many)
- AttendanceSession → AttendanceRecords (One to Many)
- Student → AttendanceRecords (One to Many)

## Mobile App Integration

### CORS Configuration
The system is pre-configured with CORS settings for mobile app integration:
- Accepts requests from common development ports
- Configurable allowed origins in settings.py

### API Authentication
Use Token Authentication for mobile apps:
1. Login via `/api/auth/login/` to get token
2. Include token in headers: `Authorization: Token <token>`

### Barcode Scanning Flow
1. Start attendance session via API
2. Mobile app scans student barcode
3. Send barcode data to `/api/attendance/record/`
4. Receive confirmation and attendance status

## Customization

### Adding New Fields
1. Update models in `attendance/models.py`
2. Create and apply migrations
3. Update serializers and admin interface

### Custom Reports
- Extend views in `attendance/views.py`
- Add new API endpoints in `attendance/urls.py`
- Create custom templates for web reports

### Barcode Customization
- Modify `generate_barcode()` method in Student model
- Support different barcode formats (Code128, EAN, etc.)

## Production Deployment

### Environment Variables
Create `.env` file with:
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=your-database-url
ALLOWED_HOSTS=your-domain.com
```

### Database
- Switch to PostgreSQL for production
- Update DATABASES setting in settings.py

### Static Files
```bash
python manage.py collectstatic
```

### Security Checklist
- Change default SECRET_KEY
- Set DEBUG=False
- Configure proper ALLOWED_HOSTS
- Use HTTPS in production
- Set up proper CORS origins

## Testing

### API Testing
Use tools like Postman or curl to test API endpoints:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kwame_asante", "password": "lecturer123"}'

# Get courses
curl -H "Authorization: Token <your-token>" \
  http://localhost:8000/api/courses/
```

### Sample Data
The system includes comprehensive sample data:
- 2 lecturers with different departments
- 5 students with generated barcodes
- 3 courses with proper enrollment
- Sample attendance session with records

## Support & Documentation

### Project Structure
- Clean separation of API and web interfaces
- Modular design for easy extension
- Comprehensive admin interface
- Ready for mobile app integration

### Code Quality
- Following Django best practices
- Proper error handling and validation
- Security considerations implemented
- Scalable database design

## License

This project is designed for educational purposes as part of HND final year project requirements.

## Contributors

Built for Accra Technical University students and faculty.