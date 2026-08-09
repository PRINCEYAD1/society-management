from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import Society, Building, Flat, ResidentProfile
from billing.models import MaintenanceChargeTemplate, Invoice
from notices.models import Notice
from amenities.models import Amenity

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo society, buildings, flats, users, and sample data.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            admin.role = User.Role.ADMIN
            admin.first_name = 'Society'
            admin.last_name = 'Admin'
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin123)'))
        else:
            admin = User.objects.get(username='admin')

        society, _ = Society.objects.get_or_create(
            name='Green Meadows CHS', defaults={'address': 'Thane, Maharashtra', 'contact_email': 'office@greenmeadows.example'}
        )
        building, _ = Building.objects.get_or_create(society=society, name='Tower A', defaults={'total_floors': 10})

        flat1, _ = Flat.objects.get_or_create(building=building, flat_number='101', defaults={'floor': 1, 'area_sqft': 950})
        flat2, _ = Flat.objects.get_or_create(building=building, flat_number='102', defaults={'floor': 1, 'area_sqft': 1050})

        if not User.objects.filter(username='resident1').exists():
            resident = User.objects.create_user('resident1', 'resident1@example.com', 'resident123')
            resident.role = User.Role.RESIDENT
            resident.first_name = 'Rahul'
            resident.last_name = 'Sharma'
            resident.save()
            ResidentProfile.objects.create(user=resident, flat=flat1, move_in_date=date.today())
            self.stdout.write(self.style.SUCCESS('Created resident user (resident1 / resident123)'))

        if not User.objects.filter(username='security1').exists():
            guard = User.objects.create_user('security1', 'security1@example.com', 'security123')
            guard.role = User.Role.SECURITY
            guard.first_name = 'Gate'
            guard.last_name = 'Guard'
            guard.save()
            self.stdout.write(self.style.SUCCESS('Created security user (security1 / security123)'))

        template, _ = MaintenanceChargeTemplate.objects.get_or_create(
            name='Monthly Maintenance', defaults={'amount': 3500, 'description': 'Standard monthly maintenance charge'}
        )
        Invoice.objects.get_or_create(
            flat=flat1, title='Monthly Maintenance - Demo', defaults={
                'amount': 3500, 'due_date': date.today() + timedelta(days=10), 'charge_template': template
            }
        )

        Notice.objects.get_or_create(
            title='Welcome to Society Manager', defaults={
                'content': 'This is a demo notice. Admins can post real updates from the Notices section.',
                'posted_by': admin, 'pinned': True,
            }
        )

        Amenity.objects.get_or_create(
            name='Clubhouse', defaults={'description': 'Community hall for events', 'capacity': 50, 'booking_fee': 500}
        )
        Amenity.objects.get_or_create(
            name='Swimming Pool', defaults={'description': 'Open 6am-9pm', 'capacity': 20, 'booking_fee': 0}
        )

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:    admin / admin123')
        self.stdout.write('  Resident: resident1 / resident123')
        self.stdout.write('  Security: security1 / security123')
