# Society Management System

A full-stack residential society management platform built with **Django**, **Django REST Framework**, **PostgreSQL**, and **Flutter**.

The project provides a centralized system for society administrators, residents, security personnel, committee members, and staff to manage day-to-day society operations from both a web application and a mobile application.

> **Security note:** This public README intentionally excludes credentials, private URLs, database connection details, signing information, secret values, internal infrastructure details, and other sensitive deployment information.

---

## Overview

The system contains three main layers:

```text
Web Application
      │
      ├── Django Backend / REST API
      │          │
      │          └── Central Database
      │
Mobile Application
```

Both the web and mobile clients use the same backend and central data source, so information created or updated from one client can be reflected in the other.

---

## Main Features

### Authentication and Role-Based Access

The platform supports multiple user roles, including:

- Admin
- Committee
- Resident
- Security
- Staff

Permissions and available functionality are controlled according to the authenticated user's role.

The mobile application uses token-based authentication and stores authentication data securely on the device.

---

## Society and Resident Management

- Society structure management
- Building management
- Flat management
- Resident management
- Resident-to-flat assignment
- Role-aware dashboards
- Society overview statistics

---

## Billing and Payments

- Maintenance charge management
- Invoice generation
- Invoice status tracking
- Payment recording
- Multiple payment methods
- Outstanding amount tracking
- Monthly collection reporting
- Expense tracking

Invoice workflows support common states such as pending, partial, paid, and overdue.

---

## Notices

Administrators can publish and manage society notices such as:

- General announcements
- Maintenance updates
- Events
- Urgent notices
- Meeting notices

The notice system can also support attachments and pinned announcements.

---

## Complaint Management

The complaint module supports:

- Complaint categories
- Priority levels
- Status tracking
- Staff assignment
- Comments and discussion workflow

This allows complaints to be tracked from creation through resolution.

---

## Visitor Management

The visitor module supports society gate operations such as:

- Visitor registration
- Resident/admin review
- Check-in
- Check-out
- Visitor history

---

## Amenities

- Amenity listing
- Booking requests
- Booking confirmation
- Booking cancellation
- Booking fee support

---

## Staff and Domestic Worker Management

- Staff directory
- Security personnel
- Housekeeping staff
- Plumber/electrician and other service staff
- Domestic worker records
- Attendance tracking

---

## Extended Operations

Additional society-management functionality includes:

- Parcels
- Vehicles
- Move-in / move-out requests
- Certificate requests
- Society events
- Meetings
- Society assets
- Vendor and AMC management
- Expenses
- Emergency contacts
- Polls and voting
- Lost & Found

---

# REST API

A dedicated Django REST API supports the Flutter application and selected web/mobile workflows.

The API includes functionality for:

- Authentication
- User profile information
- Role-specific dashboards
- Flats
- Residents
- Lost & Found
- Notices
- Complaints
- Visitors
- Invoices
- Payments
- Amenities and bookings
- Parcels
- Vehicles
- Move requests
- Domestic workers
- Attendance
- Certificate requests
- Events
- Meetings
- Assets
- Vendor/AMC records
- Expenses
- Emergency contacts
- Polls and voting

Administrative form fields that reference related records use protected lookup services so users can select readable values instead of manually entering database IDs.

---

# Flutter Mobile Application

The repository includes a Flutter mobile client for Android.

### Mobile Technology

- Flutter
- Dart
- Material Design
- HTTP-based API integration
- Secure local token storage
- Role-based navigation

### Mobile Dashboards

The mobile application includes role-specific dashboards for:

- Admin
- Resident
- Security

The admin dashboard displays useful society information such as:

- Total flats
- Total residents
- Pending invoices
- Outstanding balances
- Monthly collections
- Expenses
- Open complaints
- Visitor activity
- Parcel status
- Other operational statistics

The dashboard layout is responsive for different device sizes.

---

## Flutter Admin Modules

The mobile admin interface provides access to modules including:

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

Several modules support create, edit, view, and workflow actions directly from the mobile application.

---

## Mobile UX Improvements

The mobile application includes improvements such as:

- Secure dropdown selection for related records
- Login request validation
- Duplicate-action prevention
- Request timeout handling
- Safe API response handling
- Role-based navigation
- Session cleanup when authentication expires
- Dialog lifecycle improvements
- Safer asynchronous form submission
- Responsive dashboard cards
- Android network access configuration

---

# Technology Stack

## Backend

- Python
- Django
- Django REST Framework
- JWT-based authentication
- Gunicorn-compatible production deployment

## Database

- PostgreSQL for production use
- SQLite can be used for local development when configured

## Web Frontend

- Django Templates
- Bootstrap
- HTML
- CSS
- JavaScript

## Mobile

- Flutter
- Dart
- Material Design
- HTTP API integration
- Secure storage

## Media and Static Files

- Cloud media support
- Static-file serving support

## Development Tools

- Git
- GitHub
- Android SDK
- Android Emulator
- VS Code / Android Studio

---

# Project Structure

```text
society_management/
├── accounts/                 # users, roles and profiles
├── amenities/                # amenities and bookings
├── billing/                  # invoices and payments
├── complaints/               # complaint management
├── core/                     # society, buildings, flats and dashboards
├── mobile_api/               # REST API for the mobile application
├── notices/                  # notices and announcements
├── operations/               # extended society operations
├── staffmgmt/                # staff and attendance
├── visitors/                 # visitor workflows
├── society_management/       # Django project configuration
├── society_mobile/           # Flutter application
├── templates/                # web templates
├── static/                   # static assets
├── manage.py
└── requirements.txt
```

---

# Local Development

## Backend

Clone the repository and create a virtual environment:

```bash
git clone <repository-url>
cd society-management
python -m venv venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables locally. Never commit real secret values or production credentials.

Apply migrations:

```bash
python manage.py migrate
```

Create an administrator if needed:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

---

## Flutter

Move into the Flutter application directory:

```bash
cd society_mobile
```

Install packages:

```bash
flutter pub get
```

Check the project:

```bash
flutter analyze
```

Run on a connected emulator or device:

```bash
flutter run
```

---

# Testing

Backend checks:

```bash
python manage.py check
```

Run Django tests:

```bash
python manage.py test
```

Flutter static analysis:

```bash
flutter analyze
```

Create a release build only after local and integration testing has passed.

---

# Data Architecture

The project follows a single-source-of-truth model:

```text
Web Client ─────┐
                ├── Backend ─── Central Database
Mobile Client ──┘
```

The Flutter application does not maintain a separate primary society database. Operational data is stored centrally through the backend.

This design helps keep resident, billing, visitor, complaint, and operational information consistent across web and mobile clients.

---

# Security Practices

The project is designed with security-conscious practices including:

- Authentication required for protected API functionality
- Role-based authorization
- Secure mobile token storage
- HTTPS in production
- Environment-based configuration for secrets
- Production security headers and secure-cookie support
- Cross-origin access controls
- Input validation
- Protected administrative operations

### Never commit or publish

- Passwords
- API keys
- Secret keys
- Database credentials
- Database connection strings
- Private service URLs
- Signing passwords
- Signing key files
- Authentication tokens
- Production environment files
- Real resident or society personal data
- Private server or infrastructure configuration

Use environment variables or a secure secret manager for production secrets.

---

# Production Readiness

Before a real production launch, the project should be reviewed for:

- Production environment configuration
- Strong secret management
- Database backups and restore testing
- Authentication and authorization review
- Login throttling / brute-force protection
- API permission testing
- Upload validation
- Logging and monitoring
- Error reporting
- Data privacy
- Dependency updates
- Security testing

No application can be guaranteed to be completely immune from attack, so production security should be reviewed continuously.

---

# Current Development Status

Implemented areas include:

- Django web application
- Role-based authentication and authorization
- Society/building/flat management
- Resident management
- Billing and payments
- Notices
- Complaints
- Visitors
- Amenities
- Staff management
- Extended operations modules
- REST API
- Mobile authentication
- Role-specific mobile dashboards
- Secure lookup/dropdown workflows
- Flutter Android application
- Production-ready database architecture
- Signed Android release workflow

The project continues to be improved through testing, UI refinement, security hardening, and production-readiness work.

---

## Important

This repository is intended to document and demonstrate the application's architecture and functionality. Sensitive production configuration is deliberately not documented in this public README.