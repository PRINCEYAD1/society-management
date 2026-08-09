# Society Manager

A full-featured residential society (housing complex) management web application built with Django.

## Modules

| Module | What it does |
|---|---|
| **Accounts** | Custom user model with 5 roles: Admin, Committee, Resident, Security, Staff. Login, logout, profile editing. |
| **Core** | Society → Building → Flat hierarchy. Resident-to-flat linking. Role-aware dashboard. |
| **Billing** | Maintenance charge templates, invoices, payments (multiple methods), auto status tracking (Pending/Partial/Paid/Overdue), one-click "generate monthly bills for all flats." |
| **Notices** | Categorized announcements (General/Maintenance/Event/Urgent/Meeting), pinning, file attachments. |
| **Complaints** | Ticketing system with category, priority, status, assignment to staff, and threaded comments. |
| **Visitors** | Full gate flow: security logs an entry → resident approves/denies → security checks the visitor in → security checks them out. |
| **Amenities** | Bookable amenities (clubhouse, pool, gym...) with a request → confirm/cancel workflow and booking fees. |
| **Staff** | Staff directory (security, housekeeping, plumber, electrician, etc.) with daily attendance tracking. |

Everything is gated by role: residents only see their own flat/invoices/complaints/bookings; Admins and Committee members see and manage everything; Security only sees visitor management; Staff can be assigned complaints.

## Tech stack

- Python 3 / Django 6.1
- SQLite (default — swap `DATABASES` in `settings.py` for Postgres/MySQL in production)
- Bootstrap 5 (via CDN) for styling — no frontend build step required
- Django admin is enabled for every model as a power-user/back-office view

## Getting started

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. (Optional but recommended) Seed demo data — a sample society, buildings,
#    flats, and one user per role, plus a notice, an amenity, and an invoice.
python manage.py seed_demo

# 5. Run the dev server
python manage.py runserver
```

Then visit **http://127.0.0.1:8000/**

### Demo logins (created by `seed_demo`)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Resident | `resident1` | `resident123` |
| Security | `security1` | `security123` |

⚠️ Change these immediately if you deploy this anywhere real. You can also create your own superuser with `python manage.py createsuperuser`.

## Project layout

```
society_management/
├── accounts/       # custom User model, login/logout, profile
├── core/           # Society/Building/Flat models, dashboard, role decorator
├── billing/        # invoices, payments, charge templates
├── notices/        # announcements
├── complaints/     # tickets + comments
├── visitors/       # gate/visitor management
├── amenities/      # bookable amenities
├── staffmgmt/      # staff + attendance
├── templates/      # shared base.html + per-app templates (Bootstrap 5)
├── static/         # static assets (empty by default)
├── media/          # uploaded files (photos, attachments) — created at runtime
└── manage.py
```

## Next steps you may want to take

- **Switch to Postgres** for production — update `DATABASES` in `settings.py`.
- **Set `DEBUG = False`** and a real `SECRET_KEY` (env var) and `ALLOWED_HOSTS` before deploying.
- **Add email/SMS notifications** (e.g. notice posted, visitor at the gate, invoice due) — Django's email backend is already scaffolded to console output in dev.
- **Self-service signup for residents** — right now, an Admin creates accounts (via Django admin or a future signup view) and links them to a flat via `ResidentProfile`.
- **Payment gateway integration** (Razorpay/Stripe) if you want online payments instead of manually recorded ones.
- **REST API** — if you want a mobile app later, Django REST Framework can be layered on top of these same models with minimal changes.
