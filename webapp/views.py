from itertools import groupby
from django.shortcuts import get_object_or_404, render, redirect
from .forms import *

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import Department, Measure, Mission, Overview, StrategicInitiative, Objective, FocusArea
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from . import forms
from datetime import datetime, date
import pandas as pd
from dateutil.relativedelta import relativedelta 
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.db.models import Count
from operator import attrgetter
# from django.views.generic import View
# from .urls import render_to_pdf

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


# - Dashboard
@login_required(login_url='my-login')
def dashboard(request):        
    PAGES = 5
    CURRENT_YEAR = date.today().year
    TARGET_YEAR = date.today().year + 1
    
    
    # try:
    #     department = get_object_or_404(Department, user=request.user)
    #     department_id = department.id
    # except Department.DoesNotExist:
    #     raise handler404
    
    
    department_id = request.user.department_id   
    
    
    # my_mission = Mission.objects.all() 
    my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
    my_overview = Overview.objects.filter(department_id=department_id).last()
    my_objectives = Objective.objects.filter(department_id=department_id)
    my_focus_area = FocusArea.objects.filter(department_id=department_id)
   
    
    my_measures = Measure.objects.filter(department_id=department_id) 
    
    # grouped_measures = my_measures.values('objective_id').annotate(count=Count('id'))
    
    grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
    grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}

    
    
    
    # Pagination
    # page = Paginator(my_measures, PAGES)
    # page_list = request.GET.get('page')    
    # page = page.get_page(page_list)
    
    
    my_initiatives = StrategicInitiative.objects.filter(department_id=department_id)
    
    # Pagination for initiatives
    
    # page_initiatives = Paginator(my_initiatives, PAGES)
    # page_list_initiatives = request.GET.get('page')    
    # page_initiatives = page_initiatives.get_page(page_list_initiatives)
    
    # Quarterly data
    objective_id = Measure.objects.filter(department_id=department_id, objective_id=1)

    my_quarterly_data = QuarterlyPerformanceData.objects.filter(department_id=department_id)

    
    context = {
        'mission': my_mission,
        # 'measures': my_measures, #
        'initiatives': my_initiatives,
        'overview': my_overview, 
        'objectives': my_objectives, 
        'focus_areas': my_focus_area,
        'quarterly_data': my_quarterly_data,
        'current_year': CURRENT_YEAR,
        'target_year': TARGET_YEAR,
        'grouped_measures': grouped_measures
               
               }
    
    return render(request, 'webapp/dashboard.html', context=context)




# - Create a measure record 

@login_required(login_url='my-login')
def create_measure(request):
    
    department = Department.objects.get(id=request.user.department_id)
    # objective = Objective.objects.get(id=request.user.department_id)

    form = CreateMeasureForm(initial={
                                        'department': department,
                                    
                                    # 'objective': objective,
                                        })  

    
    if request.method == "POST":
        form = CreateMeasureForm(request.POST)
        if form.is_valid():            
            measure = form.save(commit=False)
            measure.department = department
            # measure.objective = objective
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
    # form = CreateMissionForm(initial={'department': department})
    

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
def view_quarterly_data(request):   
    quarterly_data = QuarterlyPerformanceData.objects.all()  
    
    context = {
        'quarterly_data':quarterly_data,
    } 
    
    return render(request, 'webapp/view-quarterly-data.html', context=context)

def handler404(request, exception):
    context = {}
    response = render(request, "webapp/404.html", context=context)
    response.status_code = 404
    return response



# class GeneratorPdf(View):
#     def get(self, request, *args, **kwargs):
#         pdf = render_to_pdf('report.html')
        




# - User logout

def user_logout(request):
    auth.logout(request)
    messages.success(request, "Logout success!")

    return redirect("my-login")
