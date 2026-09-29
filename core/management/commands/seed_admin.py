from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import User


class Command(BaseCommand):
    """
    Creates the default admin account from ADMIN_USERNAME / ADMIN_EMAIL /
    ADMIN_PASSWORD env vars, mirroring the Flask app's init_db() behaviour.

    Usage: python manage.py seed_admin
    """

    help = "Create the default admin user if one does not already exist."

    def handle(self, *args, **options):
        user = User.objects.filter(role="admin").first()
           
        if user:
            user.username = settings.ADMIN_USERNAME
            user.email = settings.ADMIN_EMAIL
            user.set_password(settings.ADMIN_PASSWORD)
            user.is_staff = True
            user.is_superuser= True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Admin user updated: {user.email}")
            )
            return
        user = User.objects.create_superuser(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
        )
        user.role = "admin"
        user.save(update_fields=["role"])
        self.stdout.write(self.style.SUCCESS(f"Admin user created: {user.email}"))

    # def handle(self, *args, **options):
    #     if User.objects.filter(role="admin").exists():
    #         self.stdout.write(self.style.WARNING("An admin user already exists. Skipping."))
    #         return

    #     user = User.objects.create_superuser(
    #         username=settings.ADMIN_USERNAME,
    #         email=settings.ADMIN_EMAIL,
    #         password=settings.ADMIN_PASSWORD,
    #     )
    #     user.role = "admin"
    #     user.save(update_fields=["role"])
    #     self.stdout.write(self.style.SUCCESS(f"Admin user created: {user.email}"))
