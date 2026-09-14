# Society Management System

A full-stack residential society management platform built with **Django**, **Django REST Framework**, **PostgreSQL**, and **Flutter**.

The project now includes:

- A complete Django web application for society administration and day-to-day operations
- Role-based dashboards and permissions
- A secure REST API with JWT authentication
- A Flutter Android application connected to the same backend
- Production deployment on Render
- PostgreSQL-ready production configuration
- Cloud/media support using Cloudinary

The main goal of the project is to provide one centralized system where administrators, residents, security staff, committee members, and society staff can manage society operations from both the **web application** and the **mobile application**.

---

## Live Application

Production web application:

**https://society-management-pk7x.onrender.com/**

Production API base URL:

```text
https://society-management-pk7x.onrender.com/api/
```

The Flutter mobile application is configured to communicate with the production Django REST API.

---

# System Architecture

```text
                 ┌──────────────────────┐
                 │      Web Browser     │
                 │ Django + Bootstrap 5 │
                 └──────────┬───────────┘
                            │
                            │ HTTPS
                            │
                 ┌──────────▼───────────┐
                 │     Django Backend   │
                 │  Django REST API     │
                 │ JWT Authentication   │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
      PostgreSQL       Cloudinary      Flutter App
       Database        Media/Files      Android Client
```

Both the web application and Flutter application use the same backend and database. Data created or updated from one client is therefore available to the other client.

---

# Main Features

## 1. Authentication and Role-Based Access

The system uses a custom Django user model with multiple society roles.

Supported roles include:

- Admin
- Committee
- Resident
- Security
- Staff

The application provides role-aware dashboards and restricts access according to the logged-in user's responsibilities.

Examples:

- Residents see information related to their own flat and society activity.
- Admin users can manage major society modules.
- Security users can work with visitor-related operations.
- Staff members can be assigned operational work such as complaints.

The mobile API uses **JWT authentication** through Django REST Framework Simple JWT.

Main authentication endpoints:

```text
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/profile/
```

---

# Web Application Modules

## Accounts

- Custom user model
- Login and logout
- User profiles
- Role-based access
- Resident account management

## Core Society Management

- Society management
- Building management
- Flat management
- Resident-to-flat assignment
- Role-aware dashboard
- Society overview statistics

## Billing

- Maintenance charge templates
- Invoice generation
- Individual invoice tracking
- Payment recording
- Multiple payment methods
- Invoice status handling
  - Pending
  - Partial
  - Paid
  - Overdue
- Outstanding amount tracking
- Monthly collection information

## Notices

Society administrators can publish notices such as:

- General notices
- Maintenance announcements
- Events
- Urgent notices
- Meeting notices

Notices can also support pinning and file attachments.

## Complaints

Complaint/ticket management includes:

- Complaint category
- Priority
- Status
- Staff assignment
- Comments and discussion workflow

## Visitor Management

Visitor management supports the society gate workflow, including visitor registration and tracking.

Typical flow:

```text
Security logs visitor
        ↓
Resident/Admin reviews visitor
        ↓
Visitor is checked in
        ↓
Visitor is checked out
```

## Amenities

- Amenity listing
- Booking requests
- Booking confirmation/cancellation
- Booking fee support

## Staff Management

- Staff directory
- Security staff
- Housekeeping
- Plumber
- Electrician
- Other society workers
- Attendance tracking

---

# Extended Society Operations

The application was expanded beyond the original modules to cover additional society operations.

These include:

- Parcels
- Vehicles
- Domestic workers
- Domestic worker attendance
- Move-in / move-out requests
- Certificate requests
- Society events
- Society meetings
- Society assets
- Vendor and AMC management
- Society expenses
- Emergency contacts
- Polls and voting
- Lost & Found

---

# REST API

A dedicated `mobile_api` Django application provides API access for the Flutter application.

The API uses:

- Django REST Framework
- JWT authentication
- Role-aware access control
- JSON request/response payloads
- Admin-only lookup endpoints for dropdown fields

## Dashboard APIs

```text
GET /api/dashboard/admin/
GET /api/dashboard/security/
GET /api/dashboard/resident/
```

## Secure Lookup APIs

These small lookup endpoints are used by the Flutter forms so users can select readable values instead of manually entering database IDs.

```text
GET /api/lookups/buildings/
GET /api/lookups/flats/
GET /api/lookups/invoices/
```

The lookup endpoints are protected and intended for authorized administrative workflows.

## Flat and Resident APIs

```text
GET/POST /api/flats/
GET/PUT/PATCH/DELETE /api/flats/<id>/

GET/POST /api/residents/
GET/PUT/PATCH/DELETE /api/residents/<id>/
```

## Lost & Found APIs

```text
GET/POST /api/lost-found/
GET/PUT/PATCH/DELETE /api/lost-found/<id>/
```

## Notice APIs

```text
GET/POST /api/notices/
GET/PUT/PATCH/DELETE /api/notices/<id>/
```

## Complaint APIs

```text
GET/POST /api/complaints/
GET/PUT/PATCH/DELETE /api/complaints/<id>/
```

## Visitor APIs

```text
GET/POST /api/visitors/
GET/PUT/PATCH/DELETE /api/visitors/<id>/
```

## Billing APIs

```text
GET /api/billing/invoices/
GET /api/billing/invoices/<id>/
GET/POST /api/billing/payments/
```

## Amenity APIs

```text
GET /api/amenities/
GET/POST /api/amenities/bookings/
GET/PUT/PATCH/DELETE /api/amenities/bookings/<id>/
```

## Additional Operational APIs

```text
/api/parcels/
/api/vehicles/
/api/move-requests/
/api/domestic-workers/
/api/domestic-workers/attendance/
/api/certificate-requests/
/api/events/
/api/meetings/
/api/assets/
/api/vendor-amc/
/api/expenses/
/api/emergency-contacts/
/api/polls/
```

Poll voting is available through:

```text
POST /api/polls/<id>/vote/
```

---

# Flutter Mobile Application

A Flutter mobile client is located in:

```text
society_mobile/
```

The application communicates directly with the Django REST API.

## Mobile Technology

- Flutter
- Dart
- Material UI
- `http` package for API requests
- `flutter_secure_storage` for authentication token storage
- JWT access and refresh tokens

Current Flutter application version:

```text
1.0.0+1
```

Android application ID:

```text
com.princeyadav.societymanagement
```

User-facing application name:

```text
Society Management
```

---

# Flutter Authentication Flow

```text
Login Screen
     ↓
POST /api/auth/login/
     ↓
Receive Access + Refresh Token
     ↓
Store tokens securely
     ↓
Read authenticated user role
     ↓
Open role-specific dashboard
```

The Flutter login flow also includes validation and safe handling for unsuccessful server responses.

---

# Mobile Dashboards

The Flutter application includes role-specific dashboards for:

- Admin
- Resident
- Security

The Admin dashboard includes society overview information such as:

- Total flats
- Total residents
- Pending invoices
- Outstanding amount
- Collection for the current month
- Monthly expenses
- Open complaints
- Visitors today
- Parcels waiting
- Vehicle and operational statistics

Dashboard cards are responsive so the layout can adapt to different screen sizes.

---

# Flutter Admin Modules

The Flutter admin interface provides access to modules including:

- Flats
- Residents
- Lost & Found
- Notices
- Complaints
- Visitors
- Invoices
- Payments
- Amenities
- Amenity bookings
- Parcels
- Vehicles
- Domestic workers
- Attendance
- Certificate requests
- Move requests
- Events
- Meetings
- Assets
- Vendor / AMC
- Expenses
- Emergency contacts
- Polls

Several modules support create and edit workflows directly from the mobile application.

---

# Mobile Form Improvements

The mobile application originally required raw numeric database IDs in several forms. This was improved with secure dropdown lookup APIs.

Examples:

- Building selection when creating a flat
- Flat selection when creating a resident
- Flat selection for visitors
- Flat selection for invoices
- Invoice selection for payments
- Flat selection for parcels
- Flat selection for vehicles

This provides a much more practical user experience and reduces incorrect ID entry.

---

# Mobile Stability Improvements

Several Flutter lifecycle and navigation improvements have been implemented while testing the application.

Examples include:

- Preventing duplicate login actions
- Login request timeout handling
- Safe JSON response validation
- Token and user validation
- Secure storage cleanup on expired authentication
- Mounted-context checks before navigation
- Stable dashboard navigation
- Dialog lifecycle fixes
- Safer asynchronous form submission
- Responsive dashboard card layout
- Android Internet permission configuration

The application has also been tested using the Android emulator in both debug and release builds.

---

# Android Release Configuration

The Flutter Android project has been prepared for signed release builds.

The Android package name is:

```text
com.princeyadav.societymanagement
```

Release signing uses a private upload keystore configured through:

```text
android/key.properties
android/upload-keystore.jks
```

These files are intentionally excluded from Git and must never be committed.

Example release commands:

```bash
flutter clean
flutter pub get
flutter analyze
flutter build apk --release
flutter build appbundle --release
```

Generated release files:

```text
build/app/outputs/flutter-apk/app-release.apk
build/app/outputs/bundle/release/app-release.aab
```

The AAB is intended for Google Play distribution.

---

# Production Deployment

The Django application is deployed on **Render**.

Production components include:

- Django application
- Gunicorn
- PostgreSQL
- WhiteNoise static file handling
- Cloudinary support for media
- Environment-based configuration
- HTTPS

Production dependencies include:

- Django 6.1
- Django REST Framework
- Simple JWT
- PostgreSQL driver (`psycopg2-binary`)
- Gunicorn
- WhiteNoise
- Cloudinary
- `dj-database-url`
- `python-decouple`
- `django-cors-headers`

---

# Security

Security-related implementation includes:

- JWT authentication for the mobile API
- Authentication required by default for API endpoints
- Role-aware permissions
- Secure token storage on mobile
- HTTPS production deployment
- Secure cookies when production security settings are enabled
- HSTS support
- Clickjacking protection
- Content-type protection
- CORS configuration
- Environment-based secret configuration

For production deployments, always ensure:

```text
DEBUG=False
SECRET_KEY=<strong private environment value>
DATABASE_URL=<production PostgreSQL URL>
```

Never commit production credentials, database passwords, signing keys, `key.properties`, or private keystores to GitHub.

---

# Tech Stack

## Backend

- Python
- Django 6.1
- Django REST Framework
- Simple JWT
- Gunicorn

## Database

- PostgreSQL for production
- SQLite can still be used for simple local development where configured

## Web Frontend

- Django Templates
- Bootstrap 5
- HTML
- CSS
- JavaScript

## Mobile

- Flutter
- Dart
- Material Design
- HTTP API integration
- Flutter Secure Storage

## Media and Static Files

- Cloudinary
- django-cloudinary-storage
- WhiteNoise

## Deployment

- Render
- PostgreSQL

## Development Tools

- Git
- GitHub
- Android Studio / Android SDK
- Android Emulator
- VS Code

---

# Project Structure

```text
society_management/
├── accounts/                 # users, roles, profiles and authentication
├── amenities/                # amenities and booking workflows
├── billing/                  # invoices, payments and billing logic
├── complaints/               # complaint/ticket management
├── core/                     # society, building, flat and dashboard logic
├── mobile_api/               # REST API used by the Flutter application
├── notices/                  # society notices and announcements
├── operations/               # extended society operations
├── staffmgmt/                # staff and attendance management
├── visitors/                 # visitor and gate workflows
├── society_management/       # Django project settings and root URLs
├── society_mobile/           # Flutter Android/mobile application
├── templates/                # Django HTML templates
├── static/                   # static assets
├── media/                    # uploaded media in development
├── manage.py
└── requirements.txt
```

---

# Local Backend Setup

## 1. Clone the repository

```bash
git clone https://github.com/PRINCEYAD1/society-management.git
cd society-management
```

## 2. Create a virtual environment

Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create the required environment variables for your environment.

Typical production values include:

```text
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=your-postgresql-database-url
```

Do not commit real secret values.

## 5. Apply migrations

```bash
python manage.py migrate
```

## 6. Create an administrator

```bash
python manage.py createsuperuser
```

## 7. Start Django

```bash
python manage.py runserver
```

Local web application:

```text
http://127.0.0.1:8000/
```

---

# Flutter Setup

Move into the Flutter project:

```bash
cd society_mobile
```

Install packages:

```bash
flutter pub get
```

Verify the project:

```bash
flutter analyze
```

List available devices:

```bash
flutter devices
```

Run on an Android emulator/device:

```bash
flutter run
```

For an Android emulator accessing a local Django development server, the host machine can normally be reached through:

```text
http://10.0.2.2:8000/
```

The production mobile build uses the deployed HTTPS API.

---

# Testing

Django system check:

```bash
python manage.py check
```

Example API authorization tests:

```bash
python manage.py test mobile_api.tests_lookups
```

Flutter static analysis:

```bash
flutter analyze
```

Android release build:

```bash
flutter build apk --release
```

---

# Data Strategy

The system follows a single-source-of-truth architecture.

```text
Web Application ─┐
                 ├── Django Backend ─── PostgreSQL
Flutter App ─────┘
```

The Flutter application does not maintain a separate society database. All important operational information is stored centrally through Django/PostgreSQL.

This allows data entered from the web interface to appear in the mobile application and vice versa.

For larger societies, existing resident/flat information can be imported into the central database through a validated bulk-import process rather than manually maintaining separate datasets.

---

# Current Development Status

Implemented and working areas include:

- Django web application
- Role-based access
- Society/building/flat structure
- Resident management
- Billing and payments
- Notices
- Complaints
- Visitors
- Amenities
- Staff management
- Extended operations modules
- REST API
- JWT login and refresh
- Admin/resident/security API dashboards
- Secure lookup APIs
- Flutter Android application
- Production API connection
- Secure token storage
- Android release signing setup
- Signed release APK generation
- Production deployment on Render

Ongoing release work includes final UI verification, runtime regression testing, release AAB generation, and Play Store preparation.

---

# Future Improvements

Potential future enhancements include:

- Push notifications
- Email/SMS/WhatsApp alerts
- Online payment gateway integration
- Advanced reporting and analytics
- Bulk Excel/CSV resident import interface
- Mobile image/file uploads
- Improved offline handling
- Shared production cache and API throttling
- Audit logs
- Automated database backups and restore testing
- Google Play Store publishing
- iOS build and release

---

# Important Security Notes

Do not commit any of the following:

```text
.env
SECRET_KEY
DATABASE_URL
Database passwords
Cloudinary secrets
android/key.properties
android/upload-keystore.jks
Production admin passwords
JWT credentials/tokens
```

Use environment variables and secure secret-management practices for production systems.

---

# Repository

GitHub:

**PRINCEYAD1/society-management**

This project is actively being developed as a complete web + mobile society management platform.