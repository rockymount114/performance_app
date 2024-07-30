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
from dateutil.relativedelta import relativedelta 
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.db.models import Count
from operator import attrgetter
from django.views.generic import ListView
from django.views.generic import View
from .utils import render_to_pdf
from django.template.loader import render_to_string

from django.http import JsonResponse

from io import BytesIO
import os
from xhtml2pdf import pisa
from datetime import timedelta

from django.template.loader import get_template
from django.contrib.staticfiles import finders
import json
from django.db.models import Prefetch

from django.contrib.auth.decorators import user_passes_test
from django.contrib import admin
from django.utils.text import capfirst
from django.conf import settings

from .email_utils import *
from .decorators import send_approval_email
import logging


logger = logging.getLogger(__name__)

User = get_user_model()

# - Homepage 
def home(request):
    return render(request, 'webapp/index.html')



def get_current_fiscal_year():                
    current_month = date.today().month        
    if current_month >= 7:
        fiscal_year = f'FY{date.today().year + 1}'
    else:
        fiscal_year = f'FY{date.today().year}'     
    
    return fiscal_year  

def is_within_10_minutes(timestamp):
    current_time = timezone.now()
    if timestamp == None:
        return False
    else:
        time_difference = current_time - timestamp
        
        if time_difference > timedelta(minutes=10):
            return False
        else:
            return True

def get_prev_fiscal_year():                
    current_month = date.today().month        
    if current_month >= 7:
        fiscal_year = f'FY{date.today().year}'
    else:
        fiscal_year = f'FY{date.today().year - 1}'     
    
    return fiscal_year

def get_current_fiscal_year_id():
    try:
        fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())
        fiscal_year_id = fiscal_year.id
        return fiscal_year_id
    
    except FiscalYear.DoesNotExist:
        print(f"Fiscal year do not exist")
# def get_current_quarter():
#     current_date = date.today()
#     current_month = current_date.month

#     if current_month in range(4, 7):
#         quarter = 'Q4'
#     elif current_month in range(7, 10):
#         quarter = 'Q1'
#     elif current_month in range(10, 13):
#         quarter = 'Q2'
#     else:
#         quarter = 'Q3'

#     return quarter

def get_current_quarter():
    '''show pencil icon or not'''
    current_date = date.today()
    current_month = current_date.month
    current_quarter = None

    if current_month in range(4, 7):
        current_quarter = 'Q4'
    elif current_month in range(7, 10):
        current_quarter = 'Q1'
    elif current_month in range(10, 13):
        current_quarter = 'Q2'
    else:
        current_quarter = 'Q3'
        
    quarter_start_date = date(current_date.year, (current_month - 1) // 3 * 3 + 1, 1)

    days_into_quarter = (current_date - quarter_start_date).days + 1
    
    if days_into_quarter <= 360:
        return current_quarter
    else:
        return None
    

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

    
# - Dashboard
# @login_required(login_url='my-login')
# def dashboard(request):    

#     PAGES = 5
#     CURRENT_YEAR = date.today().year
#     TARGET_YEAR = date.today().year + 1
    
#     current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())
    
#     if request.user.is_citymanager_office:
#         dept_cmo = request.user.id  
        
#         # those dept id and fiscal year is getting from the filterform
#         department_id = request.GET.get('departments') 
#         fiscal_year_id = request.GET.get('fiscal_year')      
#         submit_clicked = 'submit' in request.GET           
 
#         department = Department.objects.filter(id=department_id).first()   # for filter mission, overview title

        
#         my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
#         my_overview = Overview.objects.filter(department_id=department_id).last()
#         my_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
#         my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
#         my_measures = Measure.objects.filter(objective_id__in= my_objectives)  
#         my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)

#         d_objective_names = {}
#         for i in my_objectives:
#             d_objective_names.update({i.id:i.name})

    
#         grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
#         grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
        
        
#         # Quarterly data
#         objective_id = Measure.objects.filter(department_id=department_id, objective_id=1)
#         my_quarterly_data = QuarterlyPerformanceData.objects.filter(department_id=department_id)

#         quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
#         quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
#         quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
#         quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")

#         d1 = {}
#         for i in quarterly_data_q1:
#             d1.update({i.measure_id:i.get_percentage})

#         d2 = {}
#         for i in quarterly_data_q2:
#             d2.update({i.measure_id:i.get_percentage})
            
#         d3 = {}
#         for i in quarterly_data_q3:
#             d3.update({i.measure_id:i.get_percentage})
            
#         d4 = {}
#         for i in quarterly_data_q4:
#             d4.update({i.measure_id:i.get_percentage})

#         initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id = department_id)

#         initiative_status = {}

#         for i in initiative_detail_data:
#             initiative_status.update({i.strategic_initiative.id:i.status})

#         initiative_desc_of_s = {}

#         for i in initiative_detail_data:
#             initiative_desc_of_s.update({i.strategic_initiative.id:i.description_project_status})

#         initiative_expected_impact = {}

#         for i in initiative_detail_data:
#             initiative_expected_impact.update({i.strategic_initiative.id:i.expected_impact})

#         initiative_notes = {}

#         for i in initiative_detail_data:
#             initiative_notes.update({i.strategic_initiative.id:i.notes})

#         template = 'webapp/dashboard_performance_officer.html'

        
#         context = {
#             'form': DepartmentFilterForm(
#                 initial={
#                         'departments': department_id,
#                         'fiscal_year': fiscal_year_id
#                         }),

#             'fiscal_year_id': fiscal_year_id,
            
#             'submit_clicked': submit_clicked,
            
#             'mission': my_mission,
#             'initiatives': my_initiatives,
#             'overview': my_overview, 
#             'objectives': my_objectives, 
#             'focus_areas': my_focus_area,
#             'quarterly_data': my_quarterly_data,
#             'current_year': CURRENT_YEAR,
#             'target_year': TARGET_YEAR,
#             'grouped_measures': grouped_measures,

        
#             'quarterly_data_q1':quarterly_data_q1,
#             'quarterly_data_q2':quarterly_data_q2,
#             'quarterly_data_q3':quarterly_data_q3,
#             'quarterly_data_q4':quarterly_data_q4,
#             'd1':d1,
#             'd2':d2,
#             'd3':d3,
#             'd4':d4,
#             'd_objective_names':d_objective_names,
#             'dept_cmo': dept_cmo,
#             'department': department,
#             'initiative_status': initiative_status,
#             'initiative_desc_of_s': initiative_desc_of_s,
#             'initiative_expected_impact': initiative_expected_impact,
#             'initiative_notes':initiative_notes,
       

            

                
#                 }
#         return render(request, template, context=context)
            

            
#     else: # normal user

#         fiscal_year_id = request.GET.get('fiscal_year')      
#         submit_clicked = 'submit' in request.GET 
        
        

#         department_id = request.user.department_id 
#         dept_head = User.objects.filter(Q(is_dept_head=True) & Q(department_id=department_id))
    
#         my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
#         my_overview = Overview.objects.filter(department_id=department_id).last()
        
        
#         my_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
  
#         my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
#         my_measures = Measure.objects.filter(objective_id__in= my_objectives) 

#         my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)

#         d_objective_names = {}
#         for i in my_objectives:
#             d_objective_names.update({i.id:i.name})


    
#         grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
        
#         grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
        
        
#         # Quarterly data
#         objective_id = Measure.objects.filter(department_id=department_id, objective_id=1)
#         my_quarterly_data = QuarterlyPerformanceData.objects.filter(department_id=department_id)

#         quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
#         quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
#         quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
#         quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")

#         d1 = {}
#         for i in quarterly_data_q1:
#             d1.update({i.measure_id:i.get_percentage})

#         d2 = {}
#         for i in quarterly_data_q2:
#             d2.update({i.measure_id:i.get_percentage})
            
#         d3 = {}
#         for i in quarterly_data_q3:
#             d3.update({i.measure_id:i.get_percentage})
            
#         d4 = {}
#         for i in quarterly_data_q4:
#             d4.update({i.measure_id:i.get_percentage})

#         initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id=department_id).order_by('status','created_at')

#         initiative_status = {}

#         for i in initiative_detail_data:
#             initiative_status.update({i.strategic_initiative.id:i.status})

#         initiative_desc_of_s = {}

#         for i in initiative_detail_data:
#             initiative_desc_of_s.update({i.strategic_initiative.id:i.description_project_status})

#         initiative_expected_impact = {}

#         for i in initiative_detail_data:
#             initiative_expected_impact.update({i.strategic_initiative.id:i.expected_impact})

#         initiative_notes = {}

#         for i in initiative_detail_data:
#             initiative_notes.update({i.strategic_initiative.id:i.notes})

#         template = 'webapp/dashboard_regular_user.html'
#         context = {
#             'form': DepartmentFilterForm(),
#             'submit_clicked': submit_clicked,
#             'mission': my_mission,
#             'initiatives': my_initiatives,
#             'overview': my_overview, 
#             'objectives': my_objectives, 
#             'focus_areas': my_focus_area,
#             'quarterly_data': my_quarterly_data,
#             'current_year': CURRENT_YEAR,
#             'target_year': TARGET_YEAR,
#             'grouped_measures': grouped_measures,

        
#             'quarterly_data_q1':quarterly_data_q1,
#             'quarterly_data_q2':quarterly_data_q2,
#             'quarterly_data_q3':quarterly_data_q3,
#             'quarterly_data_q4':quarterly_data_q4,
#             'd1':d1,
#             'd2':d2,
#             'd3':d3,
#             'd4':d4,
#             'd_objective_names':d_objective_names,
        

#             'dept_head':dept_head,

#             'initiative_status': initiative_status,
#             'initiative_desc_of_s': initiative_desc_of_s,
#             'initiative_expected_impact': initiative_expected_impact,
#             'initiative_notes':initiative_notes,
            
                
#                 }
        
       
       
    
#         return render(request, template, context=context)
def is_performance_officer(user):
    return user.is_citymanager_office or user.groups.filter(name='Performance Officers').exists() 

@login_required(login_url='my-login')
def dashboard(request):
    
    CURRENT_YEAR = date.today().year
    TARGET_YEAR = date.today().year + 1
    current_fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())

    if is_performance_officer(request.user):
        template = 'webapp/dashboard_performance_officer.html'
        context = get_performance_officer_context(request, current_fiscal_year)
    else:
        template = 'webapp/dashboard_regular_user.html'
        context = get_regular_user_context(request, current_fiscal_year)
    
    context['current_year'] = CURRENT_YEAR
    context['target_year'] = TARGET_YEAR

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_citymanager_office:
            dashboard_content = render_to_string('webapp/performance_officer_dashboard_content.html', context, request=request)
        else:
            dashboard_content = render_to_string('webapp/regular_user_dashboard_content.html', context, request=request)
        
        return JsonResponse({
            'dashboard_content': dashboard_content,
            'selected_department_id': context['selected_department_id'],
            'selected_fiscal_year_id': context['selected_fiscal_year_id']
        })
    else:
        return render(request, template, context=context)
        

def get_performance_officer_context(request, current_fiscal_year):
    department_id = request.GET.get('departments')
    fiscal_year_id = request.GET.get('fiscal_year')
    current_quarter = get_current_quarter()

    if not department_id:
        # Set default department to City Manager Office
        department = Department.objects.filter(name='City Manager Office').first()
        department_id = department.id if department else None

    if not fiscal_year_id:
        # Set default fiscal year to the current fiscal year
        fiscal_year_id = current_fiscal_year.id

    try:
        fiscal_year_id = int(fiscal_year_id) if fiscal_year_id is not None else None
    except ValueError:
        fiscal_year_id = None


    # # The following code is to obtain fiscal year selected value and prev year according to the selection:
    fiscal_year_selected_name = FiscalYear.objects.get(id=fiscal_year_id).name
    prev_fiscal_year_name = f'{fiscal_year_selected_name[0:2]}{str(int(fiscal_year_selected_name[2:])-1)}'
    # print(fiscal_year_selected_name)
    # print(prev_fiscal_year_name)
    # -----------------------------------------------------------------------------------------------------------
        

    department = Department.objects.filter(id=department_id).first()

    my_mission = Mission.objects.filter(department_id=department_id).last()
    my_overview = Overview.objects.filter(department_id=department_id).last()
    my_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
    # my_focus_area = FocusArea.objects.all()
    my_focus_area = FocusArea.objects.annotate(objective_count=Count('objective', filter=Q(objective__department_id=department_id, objective__fiscal_year=fiscal_year_id)))
    my_measures = Measure.objects.filter(objective_id__in=my_objectives)

    target_rate_number = {
        m.id: m.target_number if m.is_number else m.target_rate
        for m in my_measures
    }

    my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)

    d_objective_names = {i.id: i.name for i in my_objectives}

    grouped_measures = get_grouped_measures(my_measures)
    quarterly_data = get_quarterly_data(department_id)
    initiative_data = get_initiative_data(department_id)

    context = {
        'form': DepartmentFilterForm(initial={'departments': department_id, 'fiscal_year': fiscal_year_id}, user=request.user),
        'fiscal_year_id': fiscal_year_id,
        'current_quarter': current_quarter,
        'mission': my_mission,
        'initiatives': my_initiatives,
        'overview': my_overview,
        'objectives': my_objectives,
        'focus_areas': my_focus_area,
        'grouped_measures': grouped_measures,
        'target_rate_number':target_rate_number,
        'd_objective_names': d_objective_names,
        'dept_cmo': request.user.id,
        'department': department,
        'quarterly_data_q1': quarterly_data['quarterly_data_q1'],
        'quarterly_data_q2': quarterly_data['quarterly_data_q2'],
        'quarterly_data_q3': quarterly_data['quarterly_data_q3'],
        'quarterly_data_q4': quarterly_data['quarterly_data_q4'],
        'd1': quarterly_data['d1'],
        'd2': quarterly_data['d2'],
        'd3': quarterly_data['d3'],
        'd4': quarterly_data['d4'],
        'selected_department_id': department_id,
        'selected_fiscal_year_id': fiscal_year_id,
        'show_pencil_icon': True,
        "grant_extension_to_department":True,
        'show_add_button':True,

        'fiscal_year_selected_name':fiscal_year_selected_name,
        'prev_fiscal_year_name':prev_fiscal_year_name,

        **initiative_data
    }

    return context

def get_regular_user_context(request, current_fiscal_year):
    fiscal_year_id = request.GET.get('fiscal_year')

    if not fiscal_year_id:
        # Set default fiscal year to the current fiscal year
        fiscal_year_id = current_fiscal_year.id

    try:
        fiscal_year_id = int(fiscal_year_id) if fiscal_year_id is not None else None
    except ValueError:
        fiscal_year_id = None

    current_quarter = get_current_quarter()

    if current_quarter:
        show_pencil_icon = True
    else:
        show_pencil_icon = False
        
    # show add button only is current fiscal year
    if fiscal_year_id == current_fiscal_year.id:
        show_add_button = True
    else:
        show_add_button = False


        
    prev_fiscal_year = FiscalYear.objects.get(name= get_prev_fiscal_year())

    # # The following code is to obtain fiscal year selected value and prev year according to the selection:
    fiscal_year_selected_name = FiscalYear.objects.get(id=fiscal_year_id).name
    prev_fiscal_year_name = f'{fiscal_year_selected_name[0:2]}{str(int(fiscal_year_selected_name[2:])-1)}'
    # print(fiscal_year_selected_name)
    # print(prev_fiscal_year_name)
    # -----------------------------------------------------------------------------------------------------------


    department_id = request.user.department_id
    extension_granted_at = Department.objects.get(pk=department_id).extension_granted_at
    if is_within_10_minutes(extension_granted_at) == False:
        grant_extension_to_department = False
    else:
        grant_extension_to_department = True
   


    dept_head = User.objects.filter(is_dept_head=True, department_id=department_id)


    my_mission = Mission.objects.filter(department_id=department_id).last()
    my_overview = Overview.objects.filter(department_id=department_id).last()
    my_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
    # my_focus_area = FocusArea.objects.all()
    my_focus_area = FocusArea.objects.annotate(objective_count=Count('objective', filter=Q(objective__department_id=department_id, objective__fiscal_year=fiscal_year_id)))
    my_measures = Measure.objects.filter(objective_id__in=my_objectives)

    target_rate_number = {
        m.id: m.target_number if m.is_number else m.target_rate
        for m in my_measures
    }

        

    my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)

    d_objective_names = {i.id: i.name for i in my_objectives}

    grouped_measures = get_grouped_measures(my_measures)
    quarterly_data = get_quarterly_data(department_id)
    initiative_data = get_initiative_data(department_id)

    context = {
        'form': DepartmentFilterForm(initial={'fiscal_year': fiscal_year_id}),
        'current_quarter': current_quarter,
        'show_pencil_icon': show_pencil_icon,
        'show_add_button':show_add_button,
        
        'mission': my_mission,
        'initiatives': my_initiatives,
        'overview': my_overview,
        'objectives': my_objectives,
        'focus_areas': my_focus_area,
        'grouped_measures': grouped_measures,
        'target_rate_number':target_rate_number,
        'd_objective_names': d_objective_names,
        'dept_head': dept_head,
        'quarterly_data_q1': quarterly_data['quarterly_data_q1'],
        'quarterly_data_q2': quarterly_data['quarterly_data_q2'],
        'quarterly_data_q3': quarterly_data['quarterly_data_q3'],
        'quarterly_data_q4': quarterly_data['quarterly_data_q4'],
        'd1': quarterly_data['d1'],
        'd2': quarterly_data['d2'],
        'd3': quarterly_data['d3'],
        'd4': quarterly_data['d4'],
        'selected_department_id': department_id,  
        'selected_fiscal_year_id': fiscal_year_id,
        
        "current_fiscal_year":str(current_fiscal_year)[:2] + str(current_fiscal_year)[-2:],
        "prev_fiscal_year":str(prev_fiscal_year)[:2] + str(prev_fiscal_year)[-2:],
        "grant_extension_to_department":grant_extension_to_department,

        'fiscal_year_selected_name':fiscal_year_selected_name,
        'prev_fiscal_year_name':prev_fiscal_year_name,

        **initiative_data
    }

    return context

def get_grouped_measures(measures):
    grouped_measures = sorted(measures, key=attrgetter('objective_id'))
    return {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}

def get_quarterly_data(department_id):
    quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id, quarter="Q1")
    quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id, quarter="Q2")
    quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id, quarter="Q3")
    quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id, quarter="Q4")

    d1 = {i.measure_id: i.get_percentage for i in quarterly_data_q1}
    d2 = {i.measure_id: i.get_percentage for i in quarterly_data_q2}
    d3 = {i.measure_id: i.get_percentage for i in quarterly_data_q3}
    d4 = {i.measure_id: i.get_percentage for i in quarterly_data_q4}


    return {
        'quarterly_data_q1': quarterly_data_q1,
        'quarterly_data_q2': quarterly_data_q2,
        'quarterly_data_q3': quarterly_data_q3,
        'quarterly_data_q4': quarterly_data_q4,
        'd1': d1,
        'd2': d2,
        'd3': d3,
        'd4': d4
    }

def get_initiative_data(department_id):
    initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id=department_id).order_by('status', 'created_at')

    initiative_status = {i.strategic_initiative.id: i.status for i in initiative_detail_data}
    initiative_desc_of_s = {i.strategic_initiative.id: i.description_project_status for i in initiative_detail_data}
    initiative_expected_impact = {i.strategic_initiative.id: i.expected_impact for i in initiative_detail_data}
    initiative_notes = {i.strategic_initiative.id: i.notes for i in initiative_detail_data}

    return {
        'initiative_status': initiative_status,
        'initiative_desc_of_s': initiative_desc_of_s,
        'initiative_expected_impact': initiative_expected_impact,
        'initiative_notes': initiative_notes
    }


# - Create a object record 

@login_required(login_url='my-login')
@send_approval_email('objective', 'create')
def create_objective(request):   
    department_id = request.GET.get('department_id')

    if department_id:
        department = get_object_or_404(Department, id=department_id)
    else:
        department = get_object_or_404(Department, id=request.user.department_id)

    fiscal_year = get_object_or_404(FiscalYear, name=get_current_fiscal_year())       

    if request.method == "POST":
        form = CreateObjectiveForm(request.POST, initial={'fiscal_year': fiscal_year})
        
        if form.is_valid():   
            objective = form.save(commit=False)
            objective.department = department
            objective.fiscal_year = fiscal_year
            objective.created_by = request.user.get_full_name()
            objective.save() 
            form.save_m2m()

            request.objective = objective

            logger.info(f"Objective created: {objective.id} by user: {request.user.id}")
            messages.success(request, "Your objective was created and is pending review!")
            return redirect("dashboard")
        else:
            logger.warning(f"Invalid form submission for create_objective by user: {request.user.id}")
            messages.error(request, "There was an error in your form. Please check and try again.")
    else:
        form = CreateObjectiveForm(initial={'fiscal_year': fiscal_year})  

    context = {
        'form': form,
        'department': department,
    }
    return render(request, 'webapp/create-objective.html', context=context)

# Create focus area

@login_required(login_url='my-login')
def create_focus_area(request):
    
    form = CreateFocusAreaForm() 
    if request.method == "POST":
        form = CreateFocusAreaForm(request.POST)
        if form.is_valid():   
            objective = form.save(commit=False)
            objective.created_by = request.user.get_full_name()
            objective.save() 
            messages.success(request, "Your Focus Aread was created!")
            return redirect("dashboard")
    
    context = {'form': form}
   
    
    return render(request, 'webapp/create-focus-area.html', context=context)


@login_required(login_url='my-login')
@send_approval_email('measure', 'create')
def create_measure(request):
    department_id = request.GET.get('department_id')
    fiscal_year_id = request.GET.get('fiscal_year_id')

    if department_id:
        department = get_object_or_404(Department, id=department_id)
    else:
        department = get_object_or_404(Department, id=request.user.department_id)

    if fiscal_year_id:
        fiscal_year = get_object_or_404(FiscalYear, id=fiscal_year_id)
    else:
        fiscal_year = get_object_or_404(FiscalYear, name=get_current_fiscal_year())

    logger.info(f"Creating measure for department: {department}, fiscal year: {fiscal_year}")

    if request.method == "POST":
        form = CreateMeasureForm(request.POST, user=request.user, department_id=department.id, fiscal_year_id=fiscal_year.id)
        if form.is_valid():
            measure = form.save(commit=False)
            measure.department = department
            measure.fiscal_year = fiscal_year
            measure.created_by = request.user.get_full_name()
            measure.save()

            request.measure = measure  # Set this for the decorator

            logger.info(f"Measure created: {measure.id} by user: {request.user.id}")
            messages.success(request, "Your measure was created and is pending review!")
            return redirect("dashboard")
        else:
            logger.warning(f"Invalid form submission for create_measure by user: {request.user.id}")
            messages.error(request, "There was an error in your form. Please check and try again.")
    else:
        form = CreateMeasureForm(user=request.user, department_id=department.id, fiscal_year_id=fiscal_year.id)

    context = {
        'form': form,
        'department': department,
        'fiscal_year': fiscal_year,
    }
    return render(request, 'webapp/create-measure.html', context=context)



# Create a strategic Initiative
@login_required(login_url='my-login')
def create_initiative(request):
    
    department_id = request.GET.get('department_id')
    if department_id:
        department = Department.objects.get(id=department_id)
    else:
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
            instance.created_by = request.user.get_full_name()
            instance.save() 
            messages.success(request, "Your Strategic Initiative was created!")
            return redirect("dashboard")
        
    context = {'form': form}
        
    return render(request, 'webapp/create-initiative.html', context=context)




# Create Mission statement

@login_required(login_url='my-login')
def create_mission(request):
    department_id = request.GET.get('department_id')
    if department_id:
        department = get_object_or_404(Department, id=department_id)
    else:
        department = get_object_or_404(Department, id=request.user.department_id)

    form = CreateMissionForm()
    if request.method == "POST":
        form = CreateMissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.department = department
            mission.save()
            messages.success(request, "Your mission was created successfully")
            return redirect("dashboard")

    context = {
        'form': form,
        'department': department,
    }
    return render(request, 'webapp/create-mission.html', context=context)
# Create Mission statement

@login_required(login_url='my-login')
def create_overview(request):    
    department_id = request.GET.get('department_id')
    if department_id:
        department = get_object_or_404(Department, id=department_id)
    else:
        department = get_object_or_404(Department, id=request.user.department_id)

    form = CreateOverviewForm()
    if request.method == "POST":
        form = CreateOverviewForm(request.POST)
        if form.is_valid():
            overview = form.save(commit=False)
            overview.department = department
            overview.save()
            messages.success(request, "Your overview was created successfully")
            return redirect("dashboard")
    
    context = {
        'form': form,
        'department': department,
    }    
    return render(request, 'webapp/create-overview.html', context=context)

# Create quaterly data for depterment and objectives

@login_required(login_url='my-login')
def create_quarterly_data(request,pk,quarter):
    department_id = request.GET.get('department_id')
    if department_id:
        department = Department.objects.get(id=department_id)
    else:
        department = Department.objects.get(id=request.user.department_id)


    initial_data = {
        'objective':Measure.objects.get(id=pk).objective,
        'department':department,
        'measure':Measure.objects.get(id=pk),
        'quarter':quarter,
    }
    

    objective_id = Measure.objects.get(id=pk).objective
    measure = Measure.objects.get(id=pk)
    quarter = quarter

    
    form = CreateQuarterlyPerformanceDataForm(initial=initial_data)

    if request.method=="POST":
        form=CreateQuarterlyPerformanceDataForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = department
            instance.objective = objective_id
            instance.measure = measure
            instance.quarter = quarter
            instance.created_by = request.user.get_full_name()
            instance.save() 
            messages.success(request, "Your Quaterly data was created!")
            return redirect("dashboard")    
    
    context = {'form': form,
               } 
    
    return render(request, 'webapp/create-quarterly-data.html', context=context)

from django.db.models import Sum

@login_required(login_url='my-login')
def view_quarterly_data(request,pk):   
    quarterly_data = QuarterlyPerformanceData.objects.filter(measure_id=pk)
    measure = Measure.objects.get(id=pk)

    q1_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q1").first()
    q2_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q2").first()
    q3_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q3").first()
    q4_data = QuarterlyPerformanceData.objects.filter(measure_id=pk,quarter ="Q4").first()

    # Calculate the percentages for each quarter
    if q1_data and q1_data.denominator > 0:
        q1_data.percentage = int((q1_data.numerator / q1_data.denominator) * 100)
    else:
        q1_data={}

    if q2_data and q2_data.denominator > 0:
        q2_data.percentage = int((q2_data.numerator / q2_data.denominator) * 100)
    else:
        q2_data = {}

    if q3_data and q3_data.denominator > 0:
        q3_data.percentage = int((q3_data.numerator / q3_data.denominator) * 100)
    else:
        q3_data = {}

    if q4_data and q4_data.denominator > 0:
        q4_data.percentage = int((q4_data.numerator / q4_data.denominator) * 100)
    else:
        q4_data = {}
       
    # Calculate annual_percentage 
    quarterly_percentages = [
        q1_data.percentage if q1_data else None,
        q2_data.percentage if q2_data else None,
        q3_data.percentage if q3_data else None,
        q4_data.percentage if q4_data else None,
    ]
    quarterly_percentages = [p for p in quarterly_percentages if p is not None]

    if quarterly_percentages:
        annual_percentage = int(sum(quarterly_percentages) / len(quarterly_percentages))
    else:
        annual_percentage = 0
    
    context = {
        'quarterly_data':quarterly_data,
        'measure': measure,
        'q1_data':q1_data,
        'q2_data':q2_data,
        'q3_data':q3_data,
        'q4_data':q4_data,

        'annual_percentage': annual_percentage,
        
    } 
    
    return render(request, 'webapp/view-quarterly-data.html', context=context)




def handler404(request, exception):
    context = {}
    response = render(request, "webapp/404.html", context=context)
    response.status_code = 404
    return response


# for normal user to view the pdf

class GeneratePdf(View):

    def get(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            # messages.success(request, "Only department head can generate pdf")
            return redirect('my-login')
        else:
            fiscal_year_id = request.GET.get('fiscal_year') # for selection returns FY id
            
            department_id = request.user.department_id   
            department_name = Department.objects.filter(id=department_id).last()
            
            current_fiscal_year = get_current_fiscal_year()
            
            current_quarter = get_current_quarter()

            # # The following code is to obtain fiscal year selected value and prev year according to the selection:
            fiscal_year_selected_name = FiscalYear.objects.get(id=fiscal_year_id).name
            prev_fiscal_year_name = f'{fiscal_year_selected_name[0:2]}{str(int(fiscal_year_selected_name[2:])-1)}'

           


            if not fiscal_year_id:
                fiscal_year_id = FiscalYear.objects.get(name=current_fiscal_year).id
                            
            prev_fiscal_year = FiscalYear.objects.get(name= get_prev_fiscal_year())  
            user_email = User.objects.get(department_id=department_id, pk=request.user.id)
            
            dept_head_query = {
                'department_id': department_id,
                'is_dept_head': True
            }
            
            try:
                dept_head = User.objects.get(**dept_head_query)
                dept_head_name = f"{dept_head.first_name} {dept_head.last_name}"
                dept_head_email = dept_head.email
            except User.DoesNotExist:
                dept_head_name = ''
                dept_head_email = ''
            
            image_path = finders.find('./img/city_logo.png')      
            css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
            with open(css_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()

            my_mission = Mission.objects.filter(department_id=department_id).last()              
            my_overview = Overview.objects.filter(department_id=department_id).last()
            my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=fiscal_year_id)

            objectives = Objective.objects.filter(
            department_id=department_id,
            fiscal_year_id=fiscal_year_id).prefetch_related(Prefetch('focus_area', queryset=FocusArea.objects.all()))

            my_focus_area = []
            for objective in objectives:
                my_focus_area.extend(objective.focus_area.all())

            # Remove duplicate focus areas 
            my_focus_area = list(set(my_focus_area))
            # Order focus areas alphabetically by name
            my_focus_area = sorted(my_focus_area, key=lambda x: x.name) 


            my_measures = Measure.objects.filter(objective_id__in= my_objectives, approved=True) 

            target_rate_number = {
                m.id: m.target_number if m.is_number else m.target_rate
                for m in my_measures
            }

            my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)

            d_objective_names = {}
            for i in my_objectives:
                d_objective_names.update({i.id:i.name})
                
            grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
            grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
            
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
            
            # Calculate the percentages for each quarter per measure_id
            
           
            annual_percentages = {}
            for measure in my_measures:
                measure_id = measure.id
                measure_id = measure.id
                q1_percent = float((d1.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                q2_percent = float((d2.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                q3_percent = float((d3.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                q4_percent = float((d4.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                annual_percent = (q1_percent + q2_percent + q3_percent + q4_percent) / 4
                annual_percentages[measure_id] = f"{annual_percent:0.0%}"
                    
            data = {
                "page_orientation": "landscape",
                "report_name":"Performance Report",
                "name": "City of Rocky Mount", 
                "department_name": department_name,
                "username": request.user.first_name + " " + request.user.last_name,
                "user_email": user_email,
                "dept_head_name":dept_head_name,
                "dept_head_email": dept_head_email,
                "fiscal_year": FiscalYear.objects.get(pk=fiscal_year_id),
                "current_fiscal_year":str(current_fiscal_year)[:2] + str(current_fiscal_year)[-2:],
                "prev_fiscal_year":str(prev_fiscal_year)[:2] + str(prev_fiscal_year)[-2:],
                'city_logo': image_path,
                'css_content': css_content,
                
                
                "missions": my_mission,
                "overviews": my_overview,
                "objectives": my_objectives,
                "focus_areas": my_focus_area,
                "measures": my_measures,
                "initiatives": my_initiatives,
                'target_rate_number':target_rate_number,
                
                'grouped_measures': grouped_measures,
                'quarterly_data_q1':quarterly_data_q1,
                'quarterly_data_q2':quarterly_data_q2,
                'quarterly_data_q3':quarterly_data_q3,
                'quarterly_data_q4':quarterly_data_q4,
                'd1':d1,
                'd2':d2,
                'd3':d3,
                'd4':d4,
                'annual_percentages': annual_percentages,
                'd_objective_names':d_objective_names,

                'initiative_status': initiative_status,
                'initiative_desc_of_s': initiative_desc_of_s,
                'initiative_expected_impact': initiative_expected_impact,
                'initiative_notes':initiative_notes,

                'fiscal_year_selected_name': fiscal_year_selected_name,
                'prev_fiscal_year_name':prev_fiscal_year_name,
        
            }
            pdf = render_to_pdf('webapp/report.html', data) 
            
        
            if pdf:
                response=HttpResponse(pdf,content_type='application/pdf')
                filename = "%s - Performance Report %s.pdf" % (data['department_name'], data['current_fiscal_year'])
                content = "inline; filename= %s" %(filename)
                response['Content-Disposition']=content
                return response
        return HttpResponse("Page Not Found")


# for CMO because it has two parameters such as dept & fiscal year

class GeneratePdf2(View):
    def get(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated and not request.user.is_citymanager_office:
            return redirect('my-login')
        else:
            
            department_id = request.GET.get('departments') 
            fiscal_year_id = request.GET.get('fiscal_year')  
            
            fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
            
            if not department_id or not fiscal_year:
                return redirect('dashboard')
        
            department_name = Department.objects.filter(id=department_id).last()
            
            current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())        
            prev_fiscal_year = FiscalYear.objects.get(name= get_prev_fiscal_year())  


            # # The following code is to obtain fiscal year selected value and prev year according to the selection:
            fiscal_year_selected_name = FiscalYear.objects.get(id=fiscal_year_id).name
            prev_fiscal_year_name = f'{fiscal_year_selected_name[0:2]}{str(int(fiscal_year_selected_name[2:])-1)}'
          
            
            try:
                # need to fix if has multiple members in one department, such as 3 or 4 peopele, add is_data_inputor???
                user = User.objects.get(department_id=department_id, is_manager=True)
                username = user.get_full_name()
                user_email = user.email

            except User.DoesNotExist:
                username = ""
                user_email = ""            
            
            # to check if set more than 2 dept header in one dept
            dept_head_query = {
                'department_id': department_id,
                'is_dept_head': True
            }
            
            try:
                dept_head = User.objects.get(**dept_head_query)
                dept_head_name = f"{dept_head.first_name} {dept_head.last_name}"
                dept_head_email = dept_head.email
            except User.DoesNotExist:
                dept_head_name = ''
                dept_head_email = ''
            
            image_path = finders.find('./img/city_logo.png')      
            css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
            with open(css_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()

            my_mission = Mission.objects.filter(department_id=department_id).last()              
            my_overview = Overview.objects.filter(department_id=department_id).last()
            
            my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=fiscal_year)
            
            objectives = Objective.objects.filter(
            department_id=department_id,
            fiscal_year_id=fiscal_year_id).prefetch_related(Prefetch('focus_area', queryset=FocusArea.objects.all()))

            my_focus_area = []
            for objective in objectives:
                my_focus_area.extend(objective.focus_area.all())

            # Remove duplicate focus areas 
            my_focus_area = list(set(my_focus_area))
            # Order focus areas alphabetically by name
            my_focus_area = sorted(my_focus_area, key=lambda x: x.name) 


            my_measures = Measure.objects.filter(objective_id__in= my_objectives, approved=True, fiscal_year=fiscal_year) 

            target_rate_number = {
                m.id: m.target_number if m.is_number else m.target_rate
                for m in my_measures
            }

            my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year)
            
            d_objective_names = {}
            for i in my_objectives:
                d_objective_names.update({i.id:i.name})
                
            grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
            grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
            
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
             
            # Calculate the percentages for each quarter per measure_id
            
           
            annual_percentages = {}
            for measure in my_measures:
                measure_id = measure.id
                measure_id = measure.id
                q1_percent = float((d1.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                q2_percent = float((d2.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                q3_percent = float((d3.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                q4_percent = float((d4.get(measure_id, '0') or '0').replace(' % ', '')) / 100
                annual_percent = (q1_percent + q2_percent + q3_percent + q4_percent) / 4
                annual_percentages[measure_id] = f"{annual_percent:0.0%}"

           
                
            data = {
                "page_orientation": "landscape",
                "report_name":"Performance Report",
                "name": "City of Rocky Mount", 
                "department_name": department_name,
                "username": username,
                "user_email": user_email,
                "dept_head_name":dept_head_name,
                "dept_head_email": dept_head_email,
                
                "current_fiscal_year":current_fiscal_year,
                "prev_fiscal_year":prev_fiscal_year,
                "fiscal_year": fiscal_year, # fiscal year when cmo click from dashboard form
                'city_logo': image_path,
                'css_content': css_content,
                
                
                "missions": my_mission,
                "overviews": my_overview,
                "objectives": my_objectives,
                "focus_areas": my_focus_area,
                "measures": my_measures,
                "initiatives": my_initiatives,

                'target_rate_number':target_rate_number,
                
                'grouped_measures': grouped_measures,
                'quarterly_data_q1':quarterly_data_q1,
                'quarterly_data_q2':quarterly_data_q2,
                'quarterly_data_q3':quarterly_data_q3,
                'quarterly_data_q4':quarterly_data_q4,
                'd1':d1,
                'd2':d2,
                'd3':d3,
                'd4':d4,
                'annual_percentages': annual_percentages,
                
                'd_objective_names':d_objective_names,

                'initiative_status': initiative_status,
                'initiative_desc_of_s': initiative_desc_of_s,
                'initiative_expected_impact': initiative_expected_impact,
                'initiative_notes':initiative_notes,

                'fiscal_year_selected_name': fiscal_year_selected_name,
                'prev_fiscal_year_name':prev_fiscal_year_name,
        
            }
            
            pdf = render_to_pdf('webapp/report.html',data)

            if pdf:
                response=HttpResponse(pdf,content_type='application/pdf')
                filename = "%s - Performance Report %s.pdf" % (data['department_name'], data['current_fiscal_year'])
                content = "inline; filename= %s" %(filename)
                response['Content-Disposition']=content
                return response
       

        return HttpResponse("Page Not Found")
    


# Approved Plan for everyone

class GeneratePdf3(View):
    def get(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated and not request.user.is_citymanager_office:
            return redirect('my-login')
        else:
            
            department_id = request.GET.get('departments') 
            fiscal_year_id = request.GET.get('fiscal_year')  
            
            fiscal_year = FiscalYear.objects.get(pk=fiscal_year_id)
            
            if not department_id:
                department_id = request.user.department_id   
        
            department_name = Department.objects.filter(id=department_id).last()
            
            current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())        
            prev_fiscal_year = FiscalYear.objects.get(name= get_prev_fiscal_year())  

            # # The following code is to obtain fiscal year selected value and prev year according to the selection:
            fiscal_year_selected_name = FiscalYear.objects.get(id=fiscal_year_id).name
            prev_fiscal_year_name = f'{fiscal_year_selected_name[0:2]}{str(int(fiscal_year_selected_name[2:])-1)}'

            print(fiscal_year_selected_name)
            print(prev_fiscal_year_name)
            
            try:
                # need to fix if has multiple members in one department, such as 3 or 4 peopele, add is_data_inputor???
                user = User.objects.get(department_id=department_id, is_manager=True)
                username = user.get_full_name()
                user_email = user.email

            except User.DoesNotExist:
                username = ""
                user_email = ""            
            
            # to check if set more than 2 dept header in one dept
            dept_head_query = {
                'department_id': department_id,
                'is_dept_head': True
            }
            
            try:
                dept_head = User.objects.get(**dept_head_query)
                dept_head_name = f"{dept_head.first_name} {dept_head.last_name}"
                dept_head_email = dept_head.email
            except User.DoesNotExist:
                dept_head_name = ''
                dept_head_email = ''
            
            image_path = finders.find('./img/city_logo.png')      
            css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
            with open(css_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()

            my_mission = Mission.objects.filter(department_id=department_id).last()              
            my_overview = Overview.objects.filter(department_id=department_id).last()
            
            my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=fiscal_year)
            
            objectives = Objective.objects.filter(
            department_id=department_id,
            fiscal_year_id=fiscal_year_id).prefetch_related(Prefetch('focus_area', queryset=FocusArea.objects.all()))

            my_focus_area = []
            for objective in objectives:
                my_focus_area.extend(objective.focus_area.all())

            # Remove duplicate focus areas 
            my_focus_area = list(set(my_focus_area))
            # Order focus areas alphabetically by name
            my_focus_area = sorted(my_focus_area, key=lambda x: x.name) 


            my_measures = Measure.objects.filter(objective_id__in= my_objectives, approved=True, fiscal_year=fiscal_year) 


            target_rate_number = {
                m.id: m.target_number if m.is_number else m.target_rate
                for m in my_measures
            }

            my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year)
            print(my_measures)
            
            d_objective_names = {}
            for i in my_objectives:
                d_objective_names.update({i.id:i.name})
                
            grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
            grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
            
            # quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
            # quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
            # quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
            # quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")
            
            # d1 = {}
            # for i in quarterly_data_q1:
            #     d1.update({i.measure_id:i.get_percentage})

            # d2 = {}
            # for i in quarterly_data_q2:
            #     d2.update({i.measure_id:i.get_percentage})
                
            # d3 = {}
            # for i in quarterly_data_q3:
            #     d3.update({i.measure_id:i.get_percentage})
                
            # d4 = {}
            # for i in quarterly_data_q4:
            #     d4.update({i.measure_id:i.get_percentage})

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
             
            # Calculate the percentages for each quarter per measure_id
            
           
            # annual_percentages = {}
            # for measure in my_measures:
            #     measure_id = measure.id
            #     measure_id = measure.id
            #     q1_percent = float((d1.get(measure_id, '0') or '0').replace(' % ', '')) / 100
            #     q2_percent = float((d2.get(measure_id, '0') or '0').replace(' % ', '')) / 100
            #     q3_percent = float((d3.get(measure_id, '0') or '0').replace(' % ', '')) / 100
            #     q4_percent = float((d4.get(measure_id, '0') or '0').replace(' % ', '')) / 100
            #     annual_percent = (q1_percent + q2_percent + q3_percent + q4_percent) / 4
            #     annual_percentages[measure_id] = f"{annual_percent:0.0%}"

           
                
            data = {
                "page_orientation": "landscape",
                "report_name":"Performance Plan",
                "name": "City of Rocky Mount", 
                "department_name": department_name,
                "username": username,
                "user_email": user_email,
                "dept_head_name":dept_head_name,
                "dept_head_email": dept_head_email,
                
                "current_fiscal_year":current_fiscal_year,
                "prev_fiscal_year":prev_fiscal_year,
                "fiscal_year": fiscal_year, # fiscal year when cmo click from dashboard form
                'city_logo': image_path,
                'css_content': css_content,
                
                
                "missions": my_mission,
                "overviews": my_overview,
                "objectives": my_objectives,
                "focus_areas": my_focus_area,
                "measures": my_measures,
                "initiatives": my_initiatives,
                'target_rate_number':target_rate_number,
                
                'grouped_measures': grouped_measures,
                # 'quarterly_data_q1':quarterly_data_q1,
                # 'quarterly_data_q2':quarterly_data_q2,
                # 'quarterly_data_q3':quarterly_data_q3,
                # 'quarterly_data_q4':quarterly_data_q4,
                # 'd1':d1,
                # 'd2':d2,
                # 'd3':d3,
                # 'd4':d4,
                # 'annual_percentages': annual_percentages,
                
                'd_objective_names':d_objective_names,

                'initiative_status': initiative_status,
                'initiative_desc_of_s': initiative_desc_of_s,
                'initiative_expected_impact': initiative_expected_impact,
                'initiative_notes':initiative_notes,

                'fiscal_year_selected_name': fiscal_year_selected_name,
                'prev_fiscal_year_name':prev_fiscal_year_name,
        
            }
            
            pdf = render_to_pdf('webapp/report3.html',data)

            if pdf:
                response=HttpResponse(pdf,content_type='application/pdf')
                filename = "%s - Performance Plan %s.pdf" % (data['department_name'], data['current_fiscal_year'])
                content = "inline; filename= %s" %(filename)
                response['Content-Disposition']=content
                return response
       

        return HttpResponse("Page Not Found")
    
           
# Create profile view
   

@login_required(login_url='my-login')
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            try:
                u_form.save()
                p_form.save()
                messages.success(request, f"Your account has been updated!")
            except forms.ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
            return redirect('profile')
        else:
            for field, errors in p_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'webapp/profile.html', context=context)
        
def password_reset(request):
    

    context = {}

    return render(request, 'webapp/password_reset_form.html', context=context)


@login_required(login_url='my-login')
def approvals(request):
    if request.user.is_citymanager_office:
        dept_cmo = True
    else:
        dept_cmo = False
    # Initialize session variables if they don't exist
    if 'prechecked_objectives' not in request.session:
        request.session['prechecked_objectives'] = []
    if 'prechecked_measures' not in request.session:
        request.session['prechecked_measures'] = []

    # Check if any record needs to be approved
    approve_objective = request.GET.get('approve_objective')
    approve_measure = request.GET.get('approve_measure')


    prechecked_objectives = request.session.get('prechecked_objectives', [])


    # approve
    if approve_objective:
        Objective.objects.filter(pk=int(approve_objective)).update(approved=True)

    if approve_measure:
        Measure.objects.filter(pk=int(approve_measure)).update(approved=True)

 
    if request.method == "POST":
        objectives_id_list = request.POST.getlist('objective_boxes')
        measures_id_list = request.POST.getlist('measure_boxes')
      
        
        # update the db objectives
        for id in objectives_id_list:

            Objective.objects.filter(pk=int(id)).update(approved=True)
            

        # update the db measures 
        for id in measures_id_list:
            Measure.objects.filter(pk=int(id)).update(approved=True)
        


        # Clear session variables
        request.session['prechecked_objectives'] = []
        request.session['prechecked_measures'] = []

        messages.success(request,("Your approvals were successfully submitted!"))

    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        department_id_fetched = request.GET.get('department_id')
        fiscal_year_id_fetched = request.GET.get('fiscal_year_id')
        
        objectives_pending_approval, measures_pending_approval = get_pending_approvals(department_id_fetched, fiscal_year_id_fetched)
    
        context = {
            'objectives': objectives_pending_approval,
            'measures': measures_pending_approval,
            'prechecked_objectives_json': json.dumps(request.session.get('prechecked_objectives', [])),
            'prechecked_measures_json': json.dumps(request.session.get('prechecked_measures', [])),
            'dept_cmo':dept_cmo,
            
        }
        
        return JsonResponse(context)
    
    context = {
        'form1': ApprovalsFilterForm(),

    }
    
    return render(request, 'webapp/approvals.html', context=context)


def get_pending_approvals(department_id, fiscal_year_id):
    if department_id and fiscal_year_id:
        objectives_pending_approval = list(Objective.objects.filter(approved=False, department_id=department_id, fiscal_year_id=fiscal_year_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False, department_id=department_id, fiscal_year_id=fiscal_year_id).values('id', 'title', 'objective__name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
    
    elif department_id:
        objectives_pending_approval = list(Objective.objects.filter(approved=False, department_id=department_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False, department_id=department_id).values('id', 'title', 'objective__name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
    
    elif fiscal_year_id:
        objectives_pending_approval = list(Objective.objects.filter(approved=False, fiscal_year_id=fiscal_year_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False, fiscal_year_id=fiscal_year_id).values('id', 'title', 'fiscal_year__name', 'objective__name', 'department__name', 'created_at', 'created_by'))
    
    else:
        objectives_pending_approval = list(Objective.objects.filter(approved=False).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False).values('id', 'title', 'objective__name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
    
    return objectives_pending_approval, measures_pending_approval

    
    
    
@login_required
def update_session(request):
    # Load the session data
    session_data = request.session

    if request.method == 'POST':
        
        item_type = request.POST.get('item_type')
        item_id = int(request.POST.get('item_id'))
        is_checked = request.POST.get('is_checked') == 'true'
        
        if item_type == 'objective':
            prechecked_objectives = session_data.get('prechecked_objectives', [])
            if is_checked:
                prechecked_objectives.append(item_id)
            else:
                prechecked_objectives.remove(item_id)
            session_data['prechecked_objectives'] = prechecked_objectives
        elif item_type == 'measure':
            prechecked_measures = session_data.get('prechecked_measures', [])
            if is_checked:
                prechecked_measures.append(item_id)
            else:
                prechecked_measures.remove(item_id)
            session_data['prechecked_measures'] = prechecked_measures

        # Manually save the session data
        request.session.modified = True

        return JsonResponse({'message': 'Session updated successfully'})




# Create initiative detail

@login_required(login_url='my-login')
def create_initiative_detail(request,pk):
    department_id = request.GET.get('department_id')
    if department_id:
        department = Department.objects.get(id=department_id)
    else:
        department = Department.objects.get(id=request.user.department_id)


    initial_data = {
        'department':department,
        'strategic_initiative':StrategicInitiative.objects.get(id=pk),
      
    
    }


    strategic_initiative = StrategicInitiative.objects.get(id=pk)
    

    
    form = StrategicInitiativeDetailForm(initial=initial_data)

    if request.method=="POST":
        form=StrategicInitiativeDetailForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = department
            instance.strategic_initiative = strategic_initiative
            instance.created_by = request.user.get_full_name()
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

# View Objective Info
@login_required(login_url='my-login')
def view_objective_info(request,pk):
        
    #  department = Department.objects.get(id=request.user.department_id)
     objective = Objective.objects.get(id=pk)
  
     context = {
        # 'department':department,
        'objective':objective,
        
    } 
    
     return render(request, 'webapp/view-objective-info.html', context=context)

# View Measure Info
@login_required(login_url='my-login')
def view_measure_info(request,pk):
        
    #  department = Department.objects.get(id=request.user.department_id)
     measure = Measure.objects.get(id=pk)
     target_rate_number = measure.target_number if measure.is_number else measure.target_rate
     
     context = {
        'target_rate_number':target_rate_number,
        'measure':measure,
        
    } 
    
     return render(request, 'webapp/view-measure-info.html', context=context)


# View Focus Area Info
@login_required(login_url='my-login')
def view_focus_area_info(request,pk):
        
    #  department = Department.objects.get(id=request.user.department_id)
     focus_area = FocusArea.objects.get(id=pk)
  
     context = {
        # 'department':department,
        'focus_area':focus_area,
        
    } 
    
     return render(request, 'webapp/view-focus-area-info.html', context=context)


# View Objective Info Regular 
@login_required(login_url='my-login')
def view_objective_info_regular(request,pk):
        

     objective = Objective.objects.get(id=pk)
  
     context = {
      
        'objective':objective,
        
    } 
    
     return render(request, 'webapp/view-objective-info-regular.html', context=context)


# View Objective Info Regular 
@login_required(login_url='my-login')
def view_measure_info_regular(request,pk):
        

     measure = Measure.objects.get(id=pk)
     objective = Objective.objects.get(pk=measure.objective.id)

     target_rate_number = measure.target_number if measure.is_number else measure.target_rate


     context = {
   
        'measure':measure,
        'target_rate_number':target_rate_number,
        'objective':objective,
    } 
    
     return render(request, 'webapp/view-measure-info-regular.html', context=context)



# UPDATE FORM VIEWS


# - Update an objective

@login_required(login_url='my-login')
@send_approval_email('objective', 'update')
def update_objective(request, pk):     
    objective = get_object_or_404(Objective, id=pk)
    
    if request.method == "POST":
        form = UpdateObjectiveForm(request.POST, instance=objective)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user.get_full_name()
            instance.approved = False
            instance.save()
            form.save_m2m()
            
            request.objective = instance  # Set this for the decorator
            
            logger.info(f"Objective updated: {instance.id} by user: {request.user.id}")
            messages.success(request, "Your objective was updated and is now pending approval!")
            return redirect("dashboard")
        else:
            logger.warning(f"Invalid form submission for update_objective by user: {request.user.id}")
            messages.error(request, "There was an error in your form. Please check and try again.")
    else:
        form = UpdateObjectiveForm(instance=objective)

    context = {'form': form, 'objective': objective}
    return render(request, 'webapp/update-objective.html', context=context)


# - Update a measure
@login_required(login_url='my-login')
@send_approval_email('measure', 'update')
def update_measure(request, pk):
    measure = get_object_or_404(Measure, id=pk)
    logger.debug(f"Updating measure: {measure.id}, is_number: {measure.is_number}, target_number: {measure.target_number}, target_rate: {measure.target_rate}")
    department_id = request.GET.get('department_id')
    fiscal_year_id = request.GET.get('fiscal_year_id')

    department = get_object_or_404(Department, id=department_id) if department_id else measure.department
    fiscal_year = get_object_or_404(FiscalYear, id=fiscal_year_id) if fiscal_year_id else measure.fiscal_year

    if request.method == "POST":
        form = UpdateMeasureForm(request.POST, instance=measure, user=request.user, 
                                 department_id=department.id, fiscal_year_id=fiscal_year.id)
        if form.is_valid():
            instance = form.save(commit=False)
            logger.debug(f"Form is valid. Updated values: is_number: {instance.is_number}, target_number: {instance.target_number}, target_rate: {instance.target_rate}")
            instance.department = department
            instance.fiscal_year = fiscal_year
            instance.approved = False
            instance.modified_by = request.user.get_full_name()
            
            if request.user.is_global_performance_officer or request.user.is_citymanager_office or \
               request.user.is_dept_head or request.user.department == instance.department:
                instance.save()
                
                request.measure = instance  # Set this for the decorator
                
                logger.info(f"Measure updated: {instance.id} by user: {request.user.id}")
                messages.success(request, "Your measure was updated and is now pending approval!")
                return redirect("dashboard")
            else:
                logger.warning(f"Unauthorized measure update attempt by user: {request.user.id}")
                messages.error(request, "You don't have permission to update this measure.")
        else:
            logger.warning(f"Invalid form submission for update_measure by user: {request.user.id}")
            messages.error(request, "There was an error in your form. Please check and try again.")
    else:
        form = UpdateMeasureForm(instance=measure, user=request.user, 
                                 department_id=department.id, fiscal_year_id=fiscal_year.id)

    context = {
        'form': form,
        'measure': measure,
        'department': department,
        'fiscal_year': fiscal_year,
    }
    return render(request, 'webapp/update-measure.html', context=context)
                   

@login_required(login_url='my-login')
def request_extension(request):
    # Get the department, either from the URL or the user's profile
    department_id = request.GET.get('department_id')
    if department_id:
        department = get_object_or_404(Department, id=department_id)
    elif request.user.department_id:
        department = request.user.department
    else:
        messages.error(request, "No department specified and user is not associated with a department.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ExtensionRequestForm(request.POST, initial={'department': department})
        if form.is_valid():
            extension_request = form.save(commit=False)
            extension_request.requested_by = request.user
            extension_request.department = department
            extension_request.save()
            messages.success(request, "Extension request submitted successfully.")
            return redirect("dashboard")
    else:
        form = ExtensionRequestForm(initial={'department': department})
    
    context = {
        'form': form,
        'department': department
    }
    return render(request, 'webapp/request_extension.html', context)

# Grant extension view
@login_required(login_url='my-login')
def grant_extension(request):
    if not (request.user.is_citymanager_office or request.user.is_superuser):
        messages.error(request, "You are not authorized to visit this page!")
        return redirect("dashboard")

    pending_requests = ExtensionRequest.objects.filter(status='pending')

    if request.method == "POST":
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        extension_request = get_object_or_404(ExtensionRequest, id=request_id)
        if action == 'approve':
            extension_request.approve(request.user)
            messages.success(request, f"Extension of {extension_request.requested_duration} day(s) granted to {extension_request.department.name}.")
        elif action == 'deny':
            extension_request.deny(request.user)
            messages.success(request, f"Extension request for {extension_request.department.name} has been denied.")

        return redirect("grant-extension")

    departments = Department.objects.all().order_by('name')
    for dept in departments:
        if not dept.has_active_extension:
            dept.revoke_extension()

    context = {
        'pending_requests': pending_requests,
        'departments': departments,
    }
    return render(request, 'webapp/grant_extension.html', context)

# Extension log view
@login_required(login_url='my-login')
def extension_log(request):
    if not (request.user.is_citymanager_office or request.user.is_superuser):
        messages.error(request, "You are not authorized to view this page!")
        return redirect("dashboard")

    logs = ExtensionLog.objects.all().order_by('-granted_at')
    context = {
        'logs': logs,
    }
    return render(request, 'webapp/extension_log.html', context)

# For ACM logic
@user_passes_test(lambda u: u.is_authenticated and u.is_citymanager_office or u.is_authenticated and u.is_superuser)
def admin_forms(request):
    models = [Mission, Overview, FocusArea, Objective, Measure, QuarterlyPerformanceData, StrategicInitiative, StrategicInitiativeDetail]
    model_names_path = [model.__name__ for model in models]

    d_names = {}
    for i in models:
        d_names.update({i.__name__: capfirst(i._meta.verbose_name.replace('_', ' '))})

    form = None  # Initialize form with a default value

    if request.method == 'POST':
        selected_model_name = request.POST.get('selected_model')
        selected_model = next((model for model in models if model.__name__ == selected_model_name), None)
        if selected_model:
            model_admin = admin.site._registry[selected_model]
            form = model_admin.get_form(request)(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "The model instance was successfully created!")
                return redirect('dashboard')
        
    else:
        selected_model_name = request.GET.get('model')
        selected_model = next((model for model in models if model.__name__ == selected_model_name), None)
        if selected_model:
            model_admin = admin.site._registry[selected_model]
            form = model_admin.get_form(request)()

    context = {
        'model_names_path': model_names_path,
        'd_names': d_names,
        'selected_model_name': selected_model_name,
        'form': form,
    }
    return render(request, 'webapp/admin_forms.html', context)



# - User logout

def user_logout(request):
    auth.logout(request)
    messages.success(request, "Logout success!")

    return redirect("my-login")

