from django.core.management.base import BaseCommand
from webapp.models import *
import datetime

class Command(BaseCommand):
    help = 'Transfer data to next fiscal year'

    def handle(self,*args,**kwargs):
        # STEP ONE: CREATE NEW FISCAL YEAR
        date = datetime.date.today()
        year = date.year
        fiscal_year = f'FY{str(year + 1)}' if date.month >= 7 else f'FY{str(year)}'
        
        fiscal_years_objects = FiscalYear.objects.all()
        fy_in_db = [year.name for year in fiscal_years_objects]
        
        if fiscal_year not in fy_in_db:
            current_fiscal_year, created = FiscalYear.objects.get_or_create(name=fiscal_year)
        else:
            current_fiscal_year = FiscalYear.objects.get(name=fiscal_year)
            print(fiscal_year)

        prev_fiscal_year = f'{fiscal_year[0:2]}{str(int(fiscal_year[2:])-1)}'
        prev_fiscal_year_obj = FiscalYear.objects.get(name=prev_fiscal_year)

        # STEP TWO: CREATE OBJECTS ASSOCIATED TO NEW FISCAL YEAR
        departments = Department.objects.all()

        for department in departments:
            prev_year_objectives = Objective.objects.filter(department=department, fiscal_year=prev_fiscal_year_obj, approved=True)
            prev_year_measures = Measure.objects.filter(department=department, fiscal_year=prev_fiscal_year_obj, approved=True)
            prev_year_initiatives = StrategicInitiative.objects.filter(department=department, fiscal_year=prev_fiscal_year_obj)

            # Create a dictionary to map old objective IDs to new objective IDs
            objective_id_map = {}

            # Create objectives for the next fiscal year
            for prev_objective in prev_year_objectives:
                new_objective = Objective.objects.create(
                    name=prev_objective.name,
                    department=prev_objective.department,
                    approved=prev_objective.approved,
                    fiscal_year=current_fiscal_year,
                    created_by=prev_objective.created_by,
                    modified_by=prev_objective.modified_by
                )
                new_objective.focus_area.set(prev_objective.focus_area.all())
                
                # Store the mapping of old objective ID to new objective ID
                objective_id_map[prev_objective.id] = new_objective.id

            # Create measures for the next fiscal year
            for prev_measure in prev_year_measures:
                prev_year_measures_q_data = QuarterlyPerformanceData.objects.filter(measure=prev_measure)

                if prev_measure.is_number:
                    annual_total = sum(q.numerator for q in prev_year_measures_q_data)
                    current_year_rate = annual_total
                else:
                    annual_rate = sum(q.get_percentage_int for q in prev_year_measures_q_data)
                    current_year_rate = annual_rate / 4 if prev_year_measures_q_data else 0

                # Get the new objective ID using the mapping
                new_objective_id = objective_id_map.get(prev_measure.objective_id)
                if new_objective_id:
                    new_objective = Objective.objects.get(id=new_objective_id)
                    Measure.objects.create(
                        objective=new_objective,  # Use the new objective
                        title=prev_measure.title,
                        department=prev_measure.department,
                        direction=prev_measure.direction,
                        frequency=prev_measure.frequency,
                        current_year_rate=current_year_rate,
                        target_number=prev_measure.target_number,
                        target_rate=prev_measure.target_rate,
                        fiscal_year=current_fiscal_year,
                        is_number=prev_measure.is_number,
                    )
                else:
                    self.stdout.write(self.style.WARNING(f'No new objective found for measure: {prev_measure.title}'))

            # Update initiatives to the new fiscal year
            for initiative in prev_year_initiatives:
                latest_detail = initiative.strategicinitiativedetail_set.order_by('-created_at').first()
                if not latest_detail or latest_detail.status != 'Completed':
                    initiative.fiscal_year = current_fiscal_year
                    initiative.save()

        self.stdout.write(self.style.SUCCESS('Successfully transferred data to the next fiscal year'))