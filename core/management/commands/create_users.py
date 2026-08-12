import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update default society users"

    def handle(self, *args, **options):
        User = get_user_model()

        required_vars = [
            "ADMIN_USERNAME",
            "ADMIN_PASSWORD",
            "SECURITY_USERNAME",
            "SECURITY_PASSWORD",
            "RESIDENT_USERNAME",
            "RESIDENT_PASSWORD",
        ]

        missing = [name for name in required_vars if not os.environ.get(name)]

        if missing:
            raise CommandError(
                "Missing Render environment variables: "
                + ", ".join(missing)
            )

        users = [
            {
                "username": os.environ["ADMIN_USERNAME"],
                "password": os.environ["ADMIN_PASSWORD"],
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "label": "Admin",
            },
            {
                "username": os.environ["SECURITY_USERNAME"],
                "password": os.environ["SECURITY_PASSWORD"],
                "role": "SECURITY",
                "is_staff": False,
                "is_superuser": False,
                "label": "Security",
            },
            {
                "username": os.environ["RESIDENT_USERNAME"],
                "password": os.environ["RESIDENT_PASSWORD"],
                "role": "RESIDENT",
                "is_staff": False,
                "is_superuser": False,
                "label": "Resident",
            },
        ]

        for data in users:
            user, created = User.objects.get_or_create(
                username=data["username"]
            )

            user.role = data["role"]
            user.is_staff = data["is_staff"]
            user.is_superuser = data["is_superuser"]
            user.is_active = True

            user.set_password(data["password"])
            user.save()

            # Verify password immediately
            if not user.check_password(data["password"]):
                raise CommandError(
                    f"Password verification failed for {data['label']}."
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{data['label']} user "
                    f"{'created' if created else 'updated'}: "
                    f"{data['username']} - password verified"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "All 3 production users are ready."
            )
        )