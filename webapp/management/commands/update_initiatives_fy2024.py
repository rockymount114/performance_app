from django.core.management.base import BaseCommand
from webapp.models import StrategicInitiative, FiscalYear
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Update all Strategic Initiatives to FY2024'

    def handle(self, *args, **kwargs):
        try:
            # Get FY2024
            try:
                fy2024 = FiscalYear.objects.get(name='FY2024')
            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR('FY2024 does not exist in the database. Please create it first.'))
                return

            # Get all initiatives
            initiatives = StrategicInitiative.objects.all()
            
            # Update count
            update_count = 0
            
            # Update all initiatives
            for initiative in initiatives:
                if initiative.fiscal_year != fy2024:
                    initiative.fiscal_year = fy2024
                    initiative.save()
                    update_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {update_count} initiatives to FY2024'))
            
            # Check if any initiatives were not updated (should be 0)
            remaining = StrategicInitiative.objects.exclude(fiscal_year=fy2024).count()
            if remaining > 0:
                self.stdout.write(self.style.WARNING(f'{remaining} initiatives were not updated. Please check manually.'))
            else:
                self.stdout.write(self.style.SUCCESS('All initiatives are now set to FY2024'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))