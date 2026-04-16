# Internship Hours Tracker

A Django-based internship hours tracking system with user management, hour logging, dashboard analytics, and report generation.

## Features

### [USER] User Management
- User registration & login
- Role-based access control:
  - **Intern**: Track and log hours
  - **Supervisor**: Review and approve logs (provisioned)
  - **Admin**: System administration (provisioned)
- User profile management with company and course info

### [TIME] Hour Logging System
- Log daily work hours with time in/time out
- Automatic hour calculation
- Task description for each entry
- Edit/delete draft entries
- Submit logs for supervisor review
- Status tracking (Draft, Submitted, Approved, Rejected)

### [DASHBOARD] Dashboard
- Visual progress bar showing completion percentage
- Required hours vs completed hours display
- Remaining hours calculation
- Weekly work hour summary
- Recent logs overview
- Role-specific dashboards

### [FOLDER] Reports
- Daily log reports (single day export)
- Summary reports (date range export)
- Export formats:
  - **CSV** (Excel/Google Sheets compatible)
  - **PDF** (coming soon)
- Professional report formatting

## Tech Stack

- **Backend**: Django 4.2.8
- **Frontend**: Django Templates with Tailwind CSS
- **Database**: SQLite (development)
- **Design**: Mobile-first responsive approach

## Project Structure

```
internshiptracker/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── config/                   # Project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── users/                    # User management app
│   ├── models.py            # CustomUser, InternProfile, etc.
│   ├── forms.py             # User forms
│   ├── views.py             # User views
│   ├── urls.py              # User URLs
│   └── admin.py             # Admin configuration
├── logging_app/              # Hour logging app
│   ├── models.py            # HourLog model
│   ├── forms.py             # Log entry form
│   ├── views.py             # Logging views
│   ├── urls.py              # Logging URLs
│   └── admin.py             # Admin configuration
├── reports/                  # Reports app
│   ├── models.py            # Report model
│   ├── views.py             # Report generation views
│   ├── urls.py              # Report URLs
│   └── admin.py             # Admin configuration
├── templates/               # Base templates
│   ├── base.html            # Base template with navigation
│   ├── dashboard.html       # Dashboard template
│   ├── users/               # User templates
│   ├── logging_app/         # Logging templates
│   └── reports/             # Report templates
└── static/                  # Static files (CSS, JS, images)
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone the Repository
```bash
cd internshiptracker
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Usage

### Creating Test Users

1. **Via Web Interface**:
   - Navigate to the landing page
   - Click "Register" to create an account
   - Fill in required information
   - All new accounts default to "Intern" role

2. **Via Admin Panel**:
   - Go to `http://127.0.0.1:8000/admin/`
   - Log in with superuser credentials
   - Create users and assign roles (Intern, Supervisor, Admin)

### Logging Hours

1. Log in as an intern
2. Click "[TIME] Log Hours" from the dashboard
3. Fill in the form:
   - Select date
   - Enter time in/time out
   - Describe tasks completed
4. Click "Log Hours"
5. Find the entry in "[NOTES] My Logs"
6. Submit for review when ready

### Generating Reports

1. Click "[DOC] Reports" from dashboard
2. Select report type:
   - **Daily**: Single day report
   - **Summary**: Date range report
3. Select date(s) and format (CSV available)
4. Download the generated file

### Admin Panel

Access Django admin at `/admin/`:
- Manage users and roles
- View and approve hour logs
- Manage supervisor and admin accounts
- System settings and configuration

## Role-Based Features

### Intern Features
- [CHECK] Dashboard with progress tracking
- [CHECK] Log daily hours
- [CHECK] View and edit own logs
- [CHECK] Submit logs for review
- [CHECK] Generate personal reports
- [CHECK] Profile management

### Supervisor Features (Provisioned)
- View assigned interns' logs
- Approve/reject hour logs
- Add review notes
- Dashboard overview

### Admin Features (Provisioned)
- Full system access
- User and role management
- System configuration
- All audit capabilities

## Database Models

### CustomUser
Extended Django User model with role field:
- `role`: intern, supervisor, or admin

### InternProfile
Profile information for interns:
- `course`: Course/program name
- `company`: Company/organization name
- `required_hours`: Total hours required
- `start_date`, `end_date`: Internship period

### HourLog
Daily work hour entries:
- `date`: Date worked
- `time_in`, `time_out`: Work hours
- `description`: Tasks completed
- `status`: Draft → Submitted → Approved/Rejected
- `reviewed_by`: Supervisor who reviewed (optional)

### SupervisorProfile
Profile for supervisors (base provisioning)

### AdminProfile
Profile for administrators (base provisioning)

## Future Enhancements

- [ ] PDF report generation (with reportlab/weasyprint)
- [ ] Email notifications for log submissions
- [ ] Excel (.xlsx) export option
- [ ] Monthly/weekly aggregate reports
- [ ] Supervisor approval workflow
- [ ] Team management for supervisors
- [ ] Analytics and insights
- [ ] Mobile app
- [ ] Calendar view for hours
- [ ] Hour forecasting tools

## Responsive Design

The application is built with a **mobile-first approach** using Tailwind CSS:
- **Mobile**: Full-width layouts, stacked navigation
- **Tablet**: Optimized spacing and columns
- **Desktop**: Full multi-column layouts with sidebar navigation

## Deployment Notes

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for `SECRET_KEY`
4. Set up PostgreSQL database
5. Configure static file serving
6. Use a production WSGI server (Gunicorn, etc.)
7. Enable HTTPS and security headers

## License

This project is provided as-is for internship tracking purposes.

## Support

For issues or questions, contact the development team.

---

**Happy tracking! [DASHBOARD]**
