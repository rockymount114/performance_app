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



def get_current_fiscal_year():                
    current_month = date.today().month        
    if current_month > 7:
        fiscal_year = f'FY{date.today().year + 1}'
    else:
        fiscal_year = f'FY{date.today().year}'     
    
    return fiscal_year  

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



    
    
# - Dashboard
@login_required(login_url='my-login')
def dashboard(request):    

    
    PAGES = 5
    CURRENT_YEAR = date.today().year
    TARGET_YEAR = date.today().year + 1
    
    # fiscal_years = FiscalYear.objects.all().order_by('id')
    # departments = Department.objects.all().order_by('id')
    current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())
    
    if request.user.is_citymanager_office:
        dept_cmo = request.user.id  
        
        # those dept id and fiscal year is getting from the filterform
        department_id = request.GET.get('departments') 
        fiscal_year = request.GET.get('fiscal_year')  
        
        
        
        department = Department.objects.filter(id=department_id).first()   # for filter mission, overview title
        
        my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
        my_overview = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=fiscal_year)
        my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=fiscal_year)
        my_measures = Measure.objects.filter(objective_id__in= my_objectives)  
        my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year)

        d_objective_names = {}
        for i in my_objectives:
            d_objective_names.update({i.id:i.name})
        print(d_objective_names)
    
        grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
        grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
        
        
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

        initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id = department_id)

        initiative_status = {}

        for i in initiative_detail_data:
            initiative_status.update({i.strategic_initiative.id:i.status})

        initiative_desc_of_s = {}

        for i in initiative_detail_data:
            initiative_desc_of_s.update({i.strategic_initiative.id:i.description_project_status})

        initiative_expected_impact = {}

        for i in initiative_detail_data:
            initiative_expected_impact.update({i.strategic_initiative.id:i.expected_impact})

        initiative_notes = {}

        for i in initiative_detail_data:
            initiative_notes.update({i.strategic_initiative.id:i.notes})

        
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
            'department': department,
            'initiative_status': initiative_status,
            'initiative_desc_of_s': initiative_desc_of_s,
            'initiative_expected_impact': initiative_expected_impact,
            'initiative_notes':initiative_notes,

                
                }
        return render(request, 'webapp/dashboard.html', context=context)
            

            
    else:
        
        department_id = request.user.department_id 
        dept_head = User.objects.filter(Q(is_dept_head=True) & Q(department_id=department_id))
    
        my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
        my_overview = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=current_fiscal_year.id)
        my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)
        my_measures = Measure.objects.filter(objective_id__in= my_objectives) 
        my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)
        print(my_measures)
        print(my_objectives)
        d_objective_names = {}
        for i in my_objectives:
            d_objective_names.update({i.id:i.name})

        print(d_objective_names)
    
        grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
        grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
        
        
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

        initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id=department_id).order_by('status','created_at')

        initiative_status = {}

        for i in initiative_detail_data:
            initiative_status.update({i.strategic_initiative.id:i.status})

        initiative_desc_of_s = {}

        for i in initiative_detail_data:
            initiative_desc_of_s.update({i.strategic_initiative.id:i.description_project_status})

        initiative_expected_impact = {}

        for i in initiative_detail_data:
            initiative_expected_impact.update({i.strategic_initiative.id:i.expected_impact})

        initiative_notes = {}

        for i in initiative_detail_data:
            initiative_notes.update({i.strategic_initiative.id:i.notes})

        print(initiative_status)
        
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

            'initiative_status': initiative_status,
            'initiative_desc_of_s': initiative_desc_of_s,
            'initiative_expected_impact': initiative_expected_impact,
            'initiative_notes':initiative_notes,
                
                }
    
    return render(request, 'webapp/dashboard.html', context=context)


# - Create a object record 

@login_required(login_url='my-login')
def create_objective(request):   
    
    department = Department.objects.get(id=request.user.department_id)
    fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())       

    form = CreateObjectiveForm(initial={
                                        'department': department,
                                        'fiscal_year': fiscal_year,
                                        
                                        })  

    
    if request.method == "POST":
        form = CreateObjectiveForm(request.POST)
        if form.is_valid():   
            objective = form.save(commit=False)
            objective.department = department
            objective.fiscal_year = fiscal_year
            objective.save() 
            messages.success(request, "Your objective was created and pending to review!")
            return redirect("dashboard")

            
    context = {'form': form}
   
    
    return render(request, 'webapp/create-objective.html', context=context)

# Create focus area

@login_required(login_url='my-login')
def create_focus_area(request):
    department = Department.objects.get(id=request.user.department_id)
    fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())       

    form = CreateFocusAreaForm(initial={
                                        'department': department,
                                        'fiscal_year': fiscal_year,                                        
                                        }) 
    if request.method == "POST":
        form = CreateFocusAreaForm(request.POST)
        if form.is_valid():   
            objective = form.save(commit=False)
            objective.department = department
            objective.fiscal_year = fiscal_year
            objective.save() 
            messages.success(request, "Your Focus Aread was created!")
            return redirect("dashboard")
    
    context = {'form': form}
   
    
    return render(request, 'webapp/create-focus-area.html', context=context)


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
    fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())

    form = CreateInitiativeForm(initial={
                                    'department': department,
                                    'fiscal_year': fiscal_year,
                                        })  
    

    if request.method == "POST":
        form = CreateInitiativeForm(request.POST)
        if form.is_valid():            
            instance = form.save(commit=False)
            instance.department = department
            instance.fiscal_year = fiscal_year
            instance.save() 
            messages.success(request, "Your Strategic Initiative was created!")
            return redirect("dashboard")
        
    context = {'form': form}
        
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
        user_email = User.objects.get(department_id=department_id)
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






# Create initiative detail

@login_required(login_url='my-login')
def create_initiative_detail(request,pk):

    initial_data = {
        'department':request.user.department_id,
        'strategic_initiative':StrategicInitiative.objects.get(id=pk),
      
    
    }

    department = Department.objects.get(id=request.user.department_id)
    strategic_initiative = StrategicInitiative.objects.get(id=pk)
    

    
    form = StrategicInitiativeDetailForm(initial=initial_data)

    if request.method=="POST":
        form=StrategicInitiativeDetailForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = department
            instance.strategic_initiative = strategic_initiative
            instance.save() 
            messages.success(request, "Your Quaterly data was created!")
            return redirect("dashboard")    
    
    context = {'form': form,
               } 
    
    return render(request, 'webapp/create-initiative-detail.html', context=context)


# View Initiative Detail
@login_required(login_url='my-login')
def view_initiative_detail(request,pk):
        
     department = Department.objects.get(id=request.user.department_id)
     strategic_initiative = StrategicInitiative.objects.get(id=pk)
     details = StrategicInitiativeDetail.objects.filter(strategic_initiative=pk).order_by('status','created_at')
     



    
     context = {
        'strategic_initiative':strategic_initiative,
        'details':details
        
    } 
    
     return render(request, 'webapp/view-initiative-detail.html', context=context)




# - User logout

def user_logout(request):
    auth.logout(request)
    messages.success(request, "Logout success!")

    return redirect("my-login")
