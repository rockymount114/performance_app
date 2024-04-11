from itertools import groupby
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from . forms import *
from django.db.models import Q
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import Department, Measure, Mission, Overview, StrategicInitiative, Objective, FocusArea
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from datetime import datetime, date
import pandas as pd
from dateutil.relativedelta import relativedelta 
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.db.models import Count
from operator import attrgetter
from django.views.generic import ListView
from django.views.generic import View
from .utils import render_to_pdf



User = get_user_model()

# - Homepage 
def home(request):
    return render(request, 'webapp/index.html')




# - Register a user
def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect("my-login")
    context = {'form':form}
    return render(request, 'webapp/register.html', context=context)


# - Login a user
def my_login(request):
    form = LoginForm()
    
    if request.method == "POST":
        form = LoginForm(request.POST or None)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")

    context = {'form':form}

    return render(request, 'webapp/my-login.html', context=context)



# Permission to view performance data

@login_required(login_url='my-login')
def performance_data(request):    
    if request.method == "POST":
        form = CreateQuarterlyPerformanceDataForm(request.POST or None)
        if form.is_valid():            
            if request.user.groups.filter(name='Department Heads').exists(): 
                mission = Mission.objects.filter(department=request.user.department)
                
                # overview = Overview.objects.filter(department=request.user.department)
                # objective = Objective.objects.filter(department=request.user.department)
                # focusarea = FocusArea.objects.filter(department=request.user.department)            
                # measure = Measure.objects.filter(department=request.user.department)
                # strategy_initiative = StrategicInitiative.objects.filter(department=request.user.department)
            
            elif request.user.groups.filter(name='City Managers').exists():  
                mission = Mission.objects.all()
                # overview = Overview.objects.all()
                # objective = Objective.objects.all()
                # focusarea = FocusArea.objects.all()     
                # measure = Measure.objects.all()
                # strategy_initiative = StrategicInitiative.all()            
            else:

                mission = None
                # overview = None
                # objective = None
                # focusarea = None    
                # measure = None
                # strategy_initiative = None
            print(mission)
    context = {
        'missions': 'mission',
        # 'overviews': overview, 
        # 'objectives': objective,
        # 'focusareas': focusarea,
        # 'measures': measure, 
        # 'strategy_initiatives': strategy_initiative,                
            }

    return render(request, 'webapp/performance_data.html', context=context)




# - Dashboard2
# @login_required(login_url='my-login')
# class Dashboard2(ListView):  
#     model = Department
#     template_name = 'webapp/dashboard2.html'    
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['filter'] = DepartmentFilter(self.request.GET, queryset=self.get_queryset()
          
#         )
     
        
#         return context
      

    
    
    
# - Dashboard
@login_required(login_url='my-login')
def dashboard(request):    

    
    PAGES = 5
    CURRENT_YEAR = date.today().year
    TARGET_YEAR = date.today().year + 1
    
    # fiscal_years = FiscalYear.objects.all().order_by('id')
    # departments = Department.objects.all().order_by('id')
    
    if request.user.is_citymanager_office:
        dept_cmo = request.user.id  
        department_id = request.GET.get('departments') 
        fiscal_year = request.GET.get('fiscal_year')    
        
        my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
        my_overview = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id, approved = True)
        my_focus_area = FocusArea.objects.filter(department_id=department_id)
        my_measures = Measure.objects.filter(department_id=department_id) 

        d_objective_names = {}
        for i in my_objectives:
            d_objective_names.update({i.id:i.name})
    
        grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
        grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
        my_initiatives = StrategicInitiative.objects.filter(department_id=department_id)
        
        # Quarterly data
        objective_id = Measure.objects.filter(department_id=department_id, objective_id=1)
        my_quarterly_data = QuarterlyPerformanceData.objects.filter(department_id=department_id)

        quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
        quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
        quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
        quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")

        d1 = {}
        for i in quarterly_data_q1:
            d1.update({i.measure_id:i.get_percentage})

        d2 = {}
        for i in quarterly_data_q2:
            d2.update({i.measure_id:i.get_percentage})
            
        d3 = {}
        for i in quarterly_data_q3:
            d3.update({i.measure_id:i.get_percentage})
            
        d4 = {}
        for i in quarterly_data_q4:
            d4.update({i.measure_id:i.get_percentage})
        
        context = {
            'form': DepartmentFilterForm(),
            'mission': my_mission,
            'initiatives': my_initiatives,
            'overview': my_overview, 
            'objectives': my_objectives, 
            'focus_areas': my_focus_area,
            'quarterly_data': my_quarterly_data,
            'current_year': CURRENT_YEAR,
            'target_year': TARGET_YEAR,
            'grouped_measures': grouped_measures,

        
            'quarterly_data_q1':quarterly_data_q1,
            'quarterly_data_q2':quarterly_data_q2,
            'quarterly_data_q3':quarterly_data_q3,
            'quarterly_data_q4':quarterly_data_q4,
            'd1':d1,
            'd2':d2,
            'd3':d3,
            'd4':d4,
            'd_objective_names':d_objective_names,
            'dept_cmo': dept_cmo,
        

                
                }
        return render(request, 'webapp/dashboard.html', context=context)
            

            
    else:
     
        department_id = request.user.department_id 
        dept_head = User.objects.filter(Q(is_dept_head=True) & Q(department_id=department_id))
    
        my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
        my_overview = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id, approved = True)
        my_focus_area = FocusArea.objects.filter(department_id=department_id)
        my_measures = Measure.objects.filter(department_id=department_id) 

        d_objective_names = {}
        for i in my_objectives:
            d_objective_names.update({i.id:i.name})
    
        grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
        grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
        my_initiatives = StrategicInitiative.objects.filter(department_id=department_id)
        
        # Quarterly data
        objective_id = Measure.objects.filter(department_id=department_id, objective_id=1)
        my_quarterly_data = QuarterlyPerformanceData.objects.filter(department_id=department_id)

        quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
        quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
        quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
        quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")

        d1 = {}
        for i in quarterly_data_q1:
            d1.update({i.measure_id:i.get_percentage})

        d2 = {}
        for i in quarterly_data_q2:
            d2.update({i.measure_id:i.get_percentage})
            
        d3 = {}
        for i in quarterly_data_q3:
            d3.update({i.measure_id:i.get_percentage})
            
        d4 = {}
        for i in quarterly_data_q4:
            d4.update({i.measure_id:i.get_percentage})
        
        context = {
            'mission': my_mission,
            'initiatives': my_initiatives,
            'overview': my_overview, 
            'objectives': my_objectives, 
            'focus_areas': my_focus_area,
            'quarterly_data': my_quarterly_data,
            'current_year': CURRENT_YEAR,
            'target_year': TARGET_YEAR,
            'grouped_measures': grouped_measures,

        
            'quarterly_data_q1':quarterly_data_q1,
            'quarterly_data_q2':quarterly_data_q2,
            'quarterly_data_q3':quarterly_data_q3,
            'quarterly_data_q4':quarterly_data_q4,
            'd1':d1,
            'd2':d2,
            'd3':d3,
            'd4':d4,
            'd_objective_names':d_objective_names,
        

            'dept_head':dept_head,
                
                }
    
    return render(request, 'webapp/dashboard.html', context=context)


# - Create a measure record 

@login_required(login_url='my-login')
def create_measure(request):
    
    department = Department.objects.get(id=request.user.department_id)

    form = CreateMeasureForm(initial={
                                        'department': department,
                                        })  

    
    if request.method == "POST":
        form = CreateMeasureForm(request.POST)
        if form.is_valid():            
            measure = form.save(commit=False)
            measure.department = department
            measure.save() 
            messages.success(request, "Your measure was created!")
            return redirect("dashboard")
    # else:
    #     form = CreateMeasureForm()
            
    context = {'form': form}
    print(context)
    
    return render(request, 'webapp/create-measure.html', context=context)



# Create a strategic Initiative
@login_required(login_url='my-login')
def create_initiative(request):
    
    department = Department.objects.get(id=request.user.department_id)

    form = CreateInitiativeForm(initial={
                                    'department': department,
                                        })  
    

    if request.method == "POST":
        form = CreateInitiativeForm(request.POST)
        if form.is_valid():            
            instance = form.save(commit=False)
            instance.department = department
            instance.save() 
            messages.success(request, "Your Strategic Initiative was created!")
            return redirect("dashboard")
        
    context = {'form': form}
    print(context)
    
    return render(request, 'webapp/create-initiative.html', context=context)




# Create Mission statement

@login_required(login_url='my-login')
def create_mission(request):    
    department = Department.objects.get(id=request.user.department_id)    

    if request.method=="POST":
        form=CreateMissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.department = department
            mission.save()
            messages.success(request, "Your mission was created sucessfully")
            return redirect("dashboard")
    else:
        form = CreateMissionForm()
        
    context = {'form': form}    
    return render(request, 'webapp/create-mission.html', context=context)

# Create Mission statement

@login_required(login_url='my-login')
def create_overview(request):    
    department = Department.objects.get(id=request.user.department_id)
    if request.method=="POST":
        form=CreateOverviewForm(request.POST)
        if form.is_valid():
            overview = form.save(commit=False)
            overview.department = department
            overview.save()
            messages.success(request, "Your overview was created sucessfully")
            return redirect("dashboard")
    else:
        form = CreateOverviewForm()
        
    context = {'form': form}    
    return render(request, 'webapp/create-overview.html', context=context)

# Create quaterly data for depterment and objectives

@login_required(login_url='my-login')
def create_quarterly_data(request,pk,quarter):

    initial_data = {
        'objective':Measure.objects.get(id=pk).objective,
        'department':request.user.department_id,
        'measure':Measure.objects.get(id=pk),
        'quarter':quarter,
    }
    
    department_id = Department.objects.get(id = request.user.department_id)
    objective_id = Measure.objects.get(id=pk).objective
    measure = Measure.objects.get(id=pk)
    quarter = quarter

    
    form = CreateQuarterlyPerformanceDataForm(initial=initial_data)

    if request.method=="POST":
        form=CreateQuarterlyPerformanceDataForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = department_id
            instance.objective = objective_id
            instance.measure = measure
            instance.quarter = quarter
            instance.save() 
            messages.success(request, "Your Quaterly data was created!")
            return redirect("dashboard")    
    
    context = {'form': form,
               } 
    
    return render(request, 'webapp/create-quarterly-data.html', context=context)



@login_required(login_url='my-login')
def view_quarterly_data(request,pk):   
    quarterly_data = QuarterlyPerformanceData.objects.filter(measure_id=pk)
    measure = Measure.objects.get(id=pk)

    q1_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q1").first()
    q2_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q2").first()
    q3_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q3").first()
    q4_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q4").first()

    
    context = {
        'quarterly_data':quarterly_data,
        'measure': measure,
        'q1_data':q1_data,
        'q2_data':q2_data,
        'q3_data':q3_data,
        'q4_data':q4_data,
        
    } 
    
    return render(request, 'webapp/view-quarterly-data.html', context=context)




def handler404(request, exception):
    context = {}
    response = render(request, "webapp/404.html", context=context)
    response.status_code = 404
    return response




class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        department_id = request.user.department_id
        my_missions = Mission.objects.filter(department_id=department_id).last()              
        my_overviews = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id)
        my_focus_area = FocusArea.objects.filter(department_id=department_id)
        user_email = User.objects.get(id=department_id)
        dept_head = User.objects.get(Q(is_dept_head=True) & Q(department_id=department_id))

        
        data = {
        "report_name":"Performance Report",
        "name": "City of Rocky Mount", 
        "department_name": "Technology Services",
        "username": request.user.first_name + " " + request.user.last_name,
        "user_email": user_email,
        "dept_head":User.get_head_name,
        
        
        "missions": my_missions,
        "overviews": my_overviews,
        "objectives": my_objectives,
        "focusareas": my_focus_area,
        
        }
        pdf = render_to_pdf('webapp/report.html',data)
        if pdf:
            response=HttpResponse(pdf,content_type='application/pdf')
            filename = "Report_for_%s.pdf" %(data['report_name'])
            content = "inline; filename= %s" %(filename)
            response['Content-Disposition']=content
            return response
        return HttpResponse("Page Not Found")
        
# Create profile view
    
@login_required(login_url='my-login')
def profile(request):
    department_id = request.user.department_id 

    prev_year_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=1, approved = True)

    fiscal_years =  FiscalYear.objects.all()
    
    if request.method=="POST":
        carry_next_year_ids = request.POST.getlist('boxes')
        year_selected = request.POST.get('years')
        full_data = []

        for x in carry_next_year_ids:

            row = {'name': Objective.objects.get(pk=int(x)).name, 
                   'department':Objective.objects.get(pk=int(x)).department,
                   'approved':Objective.objects.get(pk=int(x)).approved,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),
                   }
            
            full_data.append(row)

        for item in full_data:
            Objective.objects.create(**item)    


        messages.success(request,(" Your data was submitted for review! "))
        return redirect('dashboard')




    context = {
        # 'mission':prev_year_mission,
        # 'overview':prev_year_overview,
        'objectives':prev_year_objectives,
        # 'focus_areas':prev_year_focus_areas,
        # 'measures':prev_year_measures,
        # 'initiatives':prev_year_initiatives,

        "fiscal_years": fiscal_years,

    }
    
    return render(request,'webapp/profile.html', context = context)


# Create fiscal year view

@login_required(login_url='my-login')
def next_fiscal_year(request):
    # Get objects that match department > fiscal_year > approved criteria 
    department_id = request.user.department_id 
    prev_year_mission = Mission.objects.filter(department_id=department_id,fiscal_year=1)
    prev_year_overview = Overview.objects.filter(department_id=department_id,fiscal_year=1)
    prev_year_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=1, approved = True)
    prev_year_focus_areas = FocusArea.objects.filter(department_id=department_id,fiscal_year=1)
    prev_year_measures = Measure.objects.filter(department_id=department_id,fiscal_year=1)
    prev_year_initiatives = StrategicInitiative.objects.filter(department_id=department_id,fiscal_year=1)

    # Get all fiscal years at the moment 
    fiscal_years =  FiscalYear.objects.all()
    

    # Execute below when form submitted  
    if request.method=="POST":
        carry_next_year_mission_id = request.POST.getlist('boxes-mission')
        carry_next_year_overview_id = request.POST.getlist('boxes-overview')
        carry_next_year_objective_ids = request.POST.getlist('boxes-objectives')
        carry_next_year_focusarea_ids = request.POST.getlist('boxes-focus_areas')
        carry_next_year_measure_ids = request.POST.getlist('boxes-measures')
        carry_next_year_initiative_ids = request.POST.getlist('boxes-initiatives')

        year_selected = request.POST.get('years')

        # Create mission that need to be carried out the next fiscal year


        carry_next_year_mission = []

        for x in carry_next_year_mission_id:

            mission = {'name': Mission.objects.get(pk=int(x)).name, 
                   'department':Mission.objects.get(pk=int(x)).department,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),
                   }
            
            carry_next_year_mission.append(mission)

        for item in carry_next_year_mission:
            Mission.objects.create(**item)


        # Create overview that need to be carried out the next fiscal year


        carry_next_year_overview = []

        for x in carry_next_year_overview_id:

            mission = {'name': Overview.objects.get(pk=int(x)).name, 
                   'department':Overview.objects.get(pk=int(x)).department,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),
                   }
            
            carry_next_year_overview.append(mission)

        for item in carry_next_year_overview:
            Overview.objects.create(**item)


        # Create objective that need to be carried out the next fiscal year

        carry_next_year_objectives = []

        for x in carry_next_year_objective_ids:

            objective = {'name': Objective.objects.get(pk=int(x)).name, 
                   'department':Objective.objects.get(pk=int(x)).department,
                   'approved':Objective.objects.get(pk=int(x)).approved,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),
                   }
            
            carry_next_year_objectives.append(objective)

        for item in carry_next_year_objectives:
            Objective.objects.create(**item)


         # Create focus areas that need to be carried out the next fiscal year

        carry_next_year_focusareas = []

        for x in carry_next_year_focusarea_ids:

            focus_area = {'name': FocusArea.objects.get(pk=int(x)).name, 
                   'department':FocusArea.objects.get(pk=int(x)).department,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),
                   }
            
            carry_next_year_focusareas.append(focus_area)

        for item in carry_next_year_focusareas:
            FocusArea.objects.create(**item)

        # Create measure that need to be carried out the next fiscal year

        carry_next_year_measures = []

        for x in carry_next_year_measure_ids:

            measure = {
                   'objective': Measure.objects.get(pk=int(x)).objective, 
                   'title': Measure.objects.get(pk=int(x)).title, 
                   'department':Measure.objects.get(pk=int(x)).department,
                   'direction': Measure.objects.get(pk=int(x)).direction, 
                   'frequency': Measure.objects.get(pk=int(x)).frequency,
                   'current_year_rate': Measure.objects.get(pk=int(x)).current_year_rate, 
                   'target_rate': Measure.objects.get(pk=int(x)).target_rate,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),  
                   }
            
            carry_next_year_measures.append(measure)

        for item in carry_next_year_measures:
            Measure.objects.create(**item)


        # Create Initiative that need to be carried out the next fiscal year
        print(carry_next_year_initiative_ids)
        print(prev_year_initiatives)

        carry_next_year_initiatives = []

        for x in carry_next_year_initiative_ids:

            initiative = {
                   'department':StrategicInitiative.objects.get(pk=int(x)).department,
                   'title':StrategicInitiative.objects.get(pk=int(x)).title,
                   'fiscal_year': FiscalYear.objects.get(pk = year_selected),
                   }
            
            carry_next_year_initiatives.append(initiative)

        for item in carry_next_year_initiatives:
            StrategicInitiative.objects.create(**item)
           




        messages.success(request,(" Your data was submitted for review! "))
        return redirect('dashboard')




    context = {
        'mission':prev_year_mission,
        'overview':prev_year_overview,
        'objectives':prev_year_objectives,
        'focus_areas':prev_year_focus_areas,
        'measures':prev_year_measures,
        'initiatives':prev_year_initiatives,

        "fiscal_years": fiscal_years,

    }
    
    return render(request,'webapp/next-fiscal-year.html', context = context)





# - User logout

def user_logout(request):
    auth.logout(request)
    messages.success(request, "Logout success!")

    return redirect("my-login")
