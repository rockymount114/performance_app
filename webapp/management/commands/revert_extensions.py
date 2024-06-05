from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from webapp.models import Department

class Command(BaseCommand):
    help = 'Revert expired extensions'

    def handle(self, *args, **options):
        expired_time = timezone.now() - timedelta(minutes=1)
        expired_departments = Department.objects.filter(grant_ext=True, extension_granted_at__lt=expired_time)

        for department in expired_departments:
            department.grant_ext = False
            department.extension_granted_at = None
            department.save()

        self.stdout.write(self.style.SUCCESS(f'Reverted {expired_departments.count()} expired extensions.'))