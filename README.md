JobConnect — Django + MySQL

A full-stack job portal web application built with Django, Python, and MySQL. Supports three user roles — Job Seeker, Employer, and Admin — each with their own dashboard and features.

Live demo: 
https://evarasingh.pythonanywhere.com/

Features

Job Seeker — browse and search jobs, apply with a cover letter, track application status from a personal dashboard

Employer — post, edit, and remove job listings, view all applicants per listing, update application status (Pending / Reviewed / Accepted / Rejected)

Admin — manage all users, jobs, and applications from a single dashboard
Search & filters — search by keyword, location, category, and job type
Authentication — register and login by email, role-based access control on every page
Responsive UI — Bootstrap 5, works on mobile and desktop

Tech Stack
Layer       Technology
Backend     Python 3.12, Django 6.
Database    MySQL 8
Frontend    Bootstrap 5
Auth        Django built-in auth + custom email login


Project Structure

jobportal_django/
├── core/                        # Django app — all business logic
│   ├── models.py                # User, Job, Application models
│   ├── views.py                 # all page handlers (15 views)
│   ├── urls.py                  # URL routing for core app
│   ├── forms.py                 # RegisterForm, LoginForm, JobForm, ApplicationForm
│   ├── admin.py                 # Django admin panel registrations
│   ├── backends.py              # custom email-based login backend
│   ├── decorators.py            # role_required() decorator
│   ├── templatetags/            # custom template filters
│   └── management/
│       └── commands/
│           └── seed_admin.py    # creates default admin account
├── jobportal/                   # Django project config
│   ├── settings.py              # all settings (DB, static, auth, etc.)
│   ├── urls.py                  # root URL dispatcher
│   ├── wsgi.py                  # production WSGI entry point
│   └── __init__.py              # PyMySQL shim
├── templates/core/              # all HTML templates
├── static/
│   ├── css/style.css
│   └── js/main.js
├── manage.py
├── requirements.txt
├── runtime.txt
├── .env.example
└── .gitignore


Database Models

User — extends Django's AbstractUser with role (seeker / employer / admin) and company fields.

Job — belongs to an employer user. Fields: title, company, location, category, salary, description, requirements, job_type, is_active, created_at.

Application — links a seeker to a job. Fields: cover_letter, status, applied_at. Each seeker can apply to a job only once.

Local Setup Requirements
Python 3.12
MySQL 8


Steps

1. Clone the repository

bash git clone https://github.com/yourusername/jobportal_django.git
cd jobportal_django

2. Create and activate a virtual environment

bash# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate

3. Install dependencies

bash pip install -r requirements.txt

4. Create the MySQL database

Open MySQL and run:

sqlCREATE DATABASE jobportal_db CHARACTER SET utf8mb4;

5. Create your .env file

Copy the example file and fill in your values:

bash cp .env.example .env

Open .env and set:

envSECRET_KEY=your-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

MYSQL_DATABASE=jobportal_db
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
DB_SSL_REQUIRE=False

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@jobportal.com
ADMIN_PASSWORD=admin123

6. Run migrations

bash python manage.py migrate

7. Create the admin account

bash python manage.py seed_admin

8. Start the development server

bash python manage.py runserver
