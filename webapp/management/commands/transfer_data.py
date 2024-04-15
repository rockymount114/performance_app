from django.core.management.base import BaseCommand
from webapp.models import *
import datetime

class Command(BaseCommand):
    help = 'Transfer data to next fiscal year'

    def handle(self,*args,**kwargs):
        #  STEP ONE: CREATE NEW FISCAL YEAR  

         #  Create fiscal year automatically
         date = datetime.date.today()

         year = date.year

         if date.month >= 7:
              fiscal_year = f'FY{str(year + 1)}'
         else:
              fiscal_year = f'FY{str(year)}' 
            
         # Check if fiscal year in database

         fiscal_years_objects =  FiscalYear.objects.all()
         fy_in_db = [year.name for year in fiscal_years_objects]

         #  if not in db create it 
         
         if fiscal_year not in fy_in_db:
            
            FiscalYear.objects.get_or_create(
                name=fiscal_year
            )
         else:
                   
            print(fiscal_year) 

         # Find ID of prev fiscal year:
         prev_fiscal_year = f'{fiscal_year[0:2]}{str(int(fiscal_year[2:])-1)}'




         for item in fiscal_years_objects:
             if item.name == prev_fiscal_year:
                 prev_fiscal_year_id = item.id

        
        
         # STEP TWO: CREATE OBJECTS  ASSOCIATED TO NEW FISCAL YEAR

         # Get objects that match department > fiscal_year > approved criteria 
         departments = Department.objects.all()

         for department in departments: 

            prev_year_objectives = Objective.objects.filter(department_id=department.id, fiscal_year=prev_fiscal_year_id, approved = True)
            prev_year_focus_areas = FocusArea.objects.filter(department_id=department.id,fiscal_year=prev_fiscal_year_id)
            prev_year_measures = Measure.objects.filter(department_id=department.id,fiscal_year=prev_fiscal_year_id)
            prev_year_initiatives = StrategicInitiative.objects.filter(department_id=department.id,fiscal_year=prev_fiscal_year_id).exclude(status='completed')

            current_fiscal_year = FiscalYear.objects.get(name=fiscal_year)
          



             # Create objective that need to be carried out the next fiscal year

            carry_next_year_objectives = []

            for x in prev_year_objectives:

                objective = {'name': Objective.objects.get(pk = x.id).name, 
                    'department':Objective.objects.get(pk = x.id).department,
                    'approved':Objective.objects.get(pk = x.id).approved,
                    'fiscal_year': current_fiscal_year,
                    }
                
                carry_next_year_objectives.append(objective)

            for item in carry_next_year_objectives:
                Objective.objects.create(**item)


            # Create focus areas that need to be carried out the next fiscal year

            carry_next_year_focusareas = []

            for x in prev_year_focus_areas:

                focus_area = {'name': FocusArea.objects.get(pk=x.id).name, 
                    'department':FocusArea.objects.get(pk=x.id).department,
                    'fiscal_year': current_fiscal_year,
                    }
                
                carry_next_year_focusareas.append(focus_area)

            for item in carry_next_year_focusareas:
                FocusArea.objects.create(**item)

            # Create measure that need to be carried out the next fiscal year

            carry_next_year_measures = []

            for x in prev_year_measures:

                measure = {
                    'objective': Measure.objects.get(pk=x.id).objective, 
                    'title': Measure.objects.get(pk=x.id).title, 
                    'department':Measure.objects.get(pk=x.id).department,
                    'direction': Measure.objects.get(pk=x.id).direction, 
                    'frequency': Measure.objects.get(pk=x.id).frequency,
                    'current_year_rate': Measure.objects.get(pk=x.id).current_year_rate, 
                    'target_rate': Measure.objects.get(pk=x.id).target_rate,
                    'fiscal_year': current_fiscal_year,  
                    }
                
                carry_next_year_measures.append(measure)

            for item in carry_next_year_measures:
                Measure.objects.create(**item)


            # Create Initiative that need to be carried out the next fiscal year


            carry_next_year_initiatives = []

            for x in prev_year_initiatives:

                initiative = {
                    'department':StrategicInitiative.objects.get(pk=x.id).department,
                    'title':StrategicInitiative.objects.get(pk=x.id).title,
                    'fiscal_year': current_fiscal_year,
                    }
                
                carry_next_year_initiatives.append(initiative)

            for item in carry_next_year_initiatives:
                StrategicInitiative.objects.create(**item)