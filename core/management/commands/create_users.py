import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update default society users"

    def handle(self, *args, **options):
        User = get_user_model()

        admin_username = os.environ.get("ADMIN_USERNAME")
        admin_password = os.environ.get("ADMIN_PASSWORD")

        security_username = os.environ.get("SECURITY_USERNAME")
        security_password = os.environ.get("SECURITY_PASSWORD")

        resident_username = os.environ.get("RESIDENT_USERNAME")
        resident_password = os.environ.get("RESIDENT_PASSWORD")

        if admin_username and admin_password:
            admin, created = User.objects.get_or_create(
                username=admin_username,
                defaults={
                    "role": "ADMIN",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )

            admin.role = "ADMIN"
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password(admin_password)
            admin.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user {'created' if created else 'updated'}: {admin_username}"
                )
            )

        if security_username and security_password:
            security, created = User.objects.get_or_create(
                username=security_username,
                defaults={
                    "role": "SECURITY",
                    "is_staff": False,
                    "is_superuser": False,
                },
            )

            security.role = "SECURITY"
            security.is_staff = False
            security.is_superuser = False
            security.set_password(security_password)
            security.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Security user {'created' if created else 'updated'}: {security_username}"
                )
            )

        if resident_username and resident_password:
            resident, created = User.objects.get_or_create(
                username=resident_username,
                defaults={
                    "role": "RESIDENT",
                    "is_staff": False,
                    "is_superuser": False,
                },
            )

            resident.role = "RESIDENT"
            resident.is_staff = False
            resident.is_superuser = False
            resident.set_password(resident_password)
            resident.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Resident user {'created' if created else 'updated'}: {resident_username}"
                )
            )