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

from django.http import JsonResponse

from io import BytesIO
import os
from xhtml2pdf import pisa


from django.template.loader import get_template
from django.contrib.staticfiles import finders
import json


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

def get_prev_fiscal_year():                
    current_month = date.today().month        
    if current_month > 7:
        fiscal_year = f'FY{date.today().year}'
    else:
        fiscal_year = f'FY{date.today().year - 1}'     
    
    return fiscal_year

def get_current_quarter():
    current_date = date.today()
    current_month = current_date.month

    if current_month in range(4, 7):
        quarter = 'Q4'
    elif current_month in range(7, 10):
        quarter = 'Q1'
    elif current_month in range(10, 13):
        quarter = 'Q2'
    else:
        quarter = 'Q3'

    return quarter

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
@login_required(login_url='my-login')
def dashboard(request):    

    
    PAGES = 5
    CURRENT_YEAR = date.today().year
    TARGET_YEAR = date.today().year + 1
    
    current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())
    
    if request.user.is_citymanager_office:
        dept_cmo = request.user.id  
        
        # those dept id and fiscal year is getting from the filterform
        department_id = request.GET.get('departments') 
        fiscal_year_id = request.GET.get('fiscal_year')      
        submit_clicked = 'submit' in request.GET           
 
        department = Department.objects.filter(id=department_id).first()   # for filter mission, overview title

        
        my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
        my_overview = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
        my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)
        my_measures = Measure.objects.filter(objective_id__in= my_objectives)  
        my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=fiscal_year_id)

        d_objective_names = {}
        for i in my_objectives:
            d_objective_names.update({i.id:i.name})

    
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
            'form': DepartmentFilterForm(
                initial={
                        'departments': department_id,
                        'fiscal_year': fiscal_year_id
                        }),

            'fiscal_year_id': fiscal_year_id,
            
            'submit_clicked': submit_clicked,
            
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
            

            
    else: # normal user
        
        department_id = request.user.department_id 
        dept_head = User.objects.filter(Q(is_dept_head=True) & Q(department_id=department_id))
    
        my_mission = Mission.objects.filter(department_id=department_id).last()               #.latest('created_at')
        my_overview = Overview.objects.filter(department_id=department_id).last()
        my_objectives = Objective.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)
  
        my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)
        my_measures = Measure.objects.filter(objective_id__in= my_objectives) 

        my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)

        d_objective_names = {}
        for i in my_objectives:
            d_objective_names.update({i.id:i.name})


    
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
            objective.created_by = request.user.get_full_name()
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
            objective.created_by = request.user.get_full_name()
            objective.save() 
            messages.success(request, "Your Focus Aread was created!")
            return redirect("dashboard")
    
    context = {'form': form}
   
    
    return render(request, 'webapp/create-focus-area.html', context=context)


@login_required(login_url='my-login')
def create_measure(request):
    department = Department.objects.get(id=request.user.department_id)
    fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())

    if request.method == "POST":
        form = CreateMeasureForm(request.POST, user=request.user)
        if form.is_valid():
            measure = form.save(commit=False)
            measure.department = department
            measure.fiscal_year = fiscal_year
            measure.created_by = request.user.get_full_name()
            measure.save()
            messages.success(request, "Your measure was created!")
            return redirect("dashboard")
    else:
        form = CreateMeasureForm(initial={'department': department, 'fiscal_year': fiscal_year}, user=request.user)

    context = {'form': form}
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
            instance.created_by = request.user.get_full_name()
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
            fiscal_year_is = request.GET.get('fiscal_year') # for selection
            department_id = request.user.department_id   
            department_name = Department.objects.filter(id=department_id).last()
            
            current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())        
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
            my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=current_fiscal_year.id)
            my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id, approved=True)
            my_measures = Measure.objects.filter(objective_id__in= my_objectives, approved=True) 
            my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)

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
                
            data = {
                "page_orientation": "landscape",
                "report_name":"Performance Report",
                "name": "City of Rocky Mount", 
                "department_name": department_name,
                "username": request.user.first_name + " " + request.user.last_name,
                "user_email": user_email,
                "dept_head_name":dept_head_name,
                "dept_head_email": dept_head_email,
                
                "current_fiscal_year":current_fiscal_year,
                "prev_fiscal_year":prev_fiscal_year,
                'city_logo': image_path,
                'css_content': css_content,
                
                
                "missions": my_mission,
                "overviews": my_overview,
                "objectives": my_objectives,
                "focus_areas": my_focus_area,
                "measures": my_measures,
                "initiatives": my_initiatives,
                
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

                'initiative_status': initiative_status,
                'initiative_desc_of_s': initiative_desc_of_s,
                'initiative_expected_impact': initiative_expected_impact,
                'initiative_notes':initiative_notes,
        
            }
        
            pdf = render_to_pdf('webapp/report.html',data)
        
            if pdf:
                response=HttpResponse(pdf,content_type='application/pdf')
                filename = "%s - Performance Report %s.pdf" % (data['department_name'], data['current_fiscal_year'])
                content = "inline; filename= %s" %(filename)
                response['Content-Disposition']=content
                return response
        return HttpResponse("Page Not Found")


# for CMO
class GeneratePdf2(View):
    def get(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated and not request.user.is_citymanager_office:
            return redirect('my-login')
        else:
            
            department_id = request.GET.get('departments') 
            fiscal_year = request.GET.get('fiscal_year')  
            

            
            if not department_id or not fiscal_year:
                return redirect('dashboard')
        
            department_name = Department.objects.filter(id=department_id).last()
            
            current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())        
            prev_fiscal_year = FiscalYear.objects.get(name= get_prev_fiscal_year())  
            
            try:
                user = User.objects.get(department_id=department_id, is_dept_head=False)
                username = user.first_name + ' ' + user.last_name
                user_email = user.email
                
            except User.DoesNotExist:
                username = ""
                user_email = ""
            
            
            
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
            my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=fiscal_year, approved=True)
            my_measures = Measure.objects.filter(objective_id__in= my_objectives, approved=True, fiscal_year=fiscal_year) 
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

                'initiative_status': initiative_status,
                'initiative_desc_of_s': initiative_desc_of_s,
                'initiative_expected_impact': initiative_expected_impact,
                'initiative_notes':initiative_notes,
        
            }
        
            pdf = render_to_pdf('webapp/report.html',data)
        
            if pdf:
                response=HttpResponse(pdf,content_type='application/pdf')
                filename = "%s - Performance Report %s.pdf" % (data['department_name'], data['current_fiscal_year'])
                content = "inline; filename= %s" %(filename)
                response['Content-Disposition']=content
                return response
        return HttpResponse("Page Not Found")

### Render html for downloading pdf

# def render_pdf(request):
#     template_path = 'webapp/report.html'
    
#     department_id = request.user.department_id
#     department = Department.objects.filter(id=department_id).first()
#     current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())        

#     user_email = User.objects.get(department_id=department_id)
#     dept_head = User.objects.get(department_id=department_id, is_dept_head=True)        
#     dept_head_name = f"{dept_head.first_name} {dept_head.last_name}"
#     dept_head_email = User.objects.get(department_id=department_id, is_dept_head=True)        

#     my_mission = Mission.objects.filter(department_id=department_id).last()              
#     my_overview = Overview.objects.filter(department_id=department_id).last()
#     my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=current_fiscal_year.id)
#     my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)
#     my_measures = Measure.objects.filter(objective_id__in= my_objectives) 
#     my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)

#     d_objective_names = {}
#     for i in my_objectives:
#         d_objective_names.update({i.id:i.name})
        
#     grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
#     grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
    
#     quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
#     quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
#     quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
#     quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")
    
#     d1 = {}
#     for i in quarterly_data_q1:
#         d1.update({i.measure_id:i.get_percentage})

#     d2 = {}
#     for i in quarterly_data_q2:
#         d2.update({i.measure_id:i.get_percentage})
        
#     d3 = {}
#     for i in quarterly_data_q3:
#         d3.update({i.measure_id:i.get_percentage})
        
#     d4 = {}
#     for i in quarterly_data_q4:
#         d4.update({i.measure_id:i.get_percentage})

#     initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id = department_id)

#     initiative_status = {}

#     for i in initiative_detail_data:
#         initiative_status.update({i.strategic_initiative.id:i.status})

#     initiative_desc_of_s = {}

#     for i in initiative_detail_data:
#         initiative_desc_of_s.update({i.strategic_initiative.id:i.description_project_status})

#     initiative_expected_impact = {}

#     for i in initiative_detail_data:
#         initiative_expected_impact.update({i.strategic_initiative.id:i.expected_impact})

#     initiative_notes = {}

#     for i in initiative_detail_data:
#         initiative_notes.update({i.strategic_initiative.id:i.notes})
            
#     context = {
        
#                 "report_name":"Performance Report",
#                 "name": department,
#                 'department': department,
#                 "department_name": department,
#                 "username": request.user.first_name + " " + request.user.last_name,
#                 "user_email": user_email,
#                 "dept_head_name":dept_head_name,
#                 "dept_head_email":dept_head_email,
                
                
#                 "missions": my_mission,
#                 "overviews": my_overview,
#                 "objectives": my_objectives,
#                 "focus_areas": my_focus_area,
#                 "measures": my_measures,
#                 "initiatives": my_initiatives,
                
#                 'grouped_measures': grouped_measures,
#                 'quarterly_data_q1':quarterly_data_q1,
#                 'quarterly_data_q2':quarterly_data_q2,
#                 'quarterly_data_q3':quarterly_data_q3,
#                 'quarterly_data_q4':quarterly_data_q4,
#                 'd1':d1,
#                 'd2':d2,
#                 'd3':d3,
#                 'd4':d4,
#                 'd_objective_names':d_objective_names,

#                 'initiative_status': initiative_status,
#                 'initiative_desc_of_s': initiative_desc_of_s,
#                 'initiative_expected_impact': initiative_expected_impact,
#                 'initiative_notes':initiative_notes,
#     }

#     return render(request,'webapp/report.html', context = context)


# For download pdf automaticlly

# @login_required(login_url='my-login')
# def render_pdf_view(request):
#     template_path = 'webapp/report.html'
#     department_id = request.user.department_id
#     department = Department.objects.filter(id=department_id).first()
#     current_fiscal_year = FiscalYear.objects.get(name= get_current_fiscal_year())        

#     user_email = User.objects.get(department_id=department_id)
#     dept_head = User.objects.get(Q(is_dept_head=True) & Q(department_id=department_id))        

#     my_mission = Mission.objects.filter(department_id=department_id).last()              
#     my_overview = Overview.objects.filter(department_id=department_id).last()
#     my_objectives = Objective.objects.filter(department_id=department_id, approved=True, fiscal_year=current_fiscal_year.id)
#     my_focus_area = FocusArea.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)
#     my_measures = Measure.objects.filter(objective_id__in= my_objectives) 
#     my_initiatives = StrategicInitiative.objects.filter(department_id=department_id, fiscal_year=current_fiscal_year.id)

#     d_objective_names = {}
#     for i in my_objectives:
#         d_objective_names.update({i.id:i.name})
        
#     grouped_measures = sorted(my_measures, key=attrgetter('objective_id'))
#     grouped_measures = {objective_id: list(measures) for objective_id, measures in groupby(grouped_measures, key=attrgetter('objective_id'))}
    
#     quarterly_data_q1 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q1")
#     quarterly_data_q2 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q2")
#     quarterly_data_q3 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q3")
#     quarterly_data_q4 = QuarterlyPerformanceData.objects.filter(department_id=department_id,quarter="Q4")
    
#     d1 = {}
#     for i in quarterly_data_q1:
#         d1.update({i.measure_id:i.get_percentage})

#     d2 = {}
#     for i in quarterly_data_q2:
#         d2.update({i.measure_id:i.get_percentage})
        
#     d3 = {}
#     for i in quarterly_data_q3:
#         d3.update({i.measure_id:i.get_percentage})
        
#     d4 = {}
#     for i in quarterly_data_q4:
#         d4.update({i.measure_id:i.get_percentage})

#     initiative_detail_data = StrategicInitiativeDetail.objects.filter(department_id = department_id)

#     initiative_status = {}

#     for i in initiative_detail_data:
#         initiative_status.update({i.strategic_initiative.id:i.status})

#     initiative_desc_of_s = {}

#     for i in initiative_detail_data:
#         initiative_desc_of_s.update({i.strategic_initiative.id:i.description_project_status})

#     initiative_expected_impact = {}

#     for i in initiative_detail_data:
#         initiative_expected_impact.update({i.strategic_initiative.id:i.expected_impact})

#     initiative_notes = {}

#     for i in initiative_detail_data:
#         initiative_notes.update({i.strategic_initiative.id:i.notes})
            
#     context = {
        
#                 "report_name":"Performance Report",
#                 "name": department,
#                 'department': department,
#                 "department_name": department,
#                 "username": request.user.first_name + " " + request.user.last_name,
#                 "user_email": user_email,
#                 "dept_head":User.get_head_name,
                
                
#                 "missions": my_mission,
#                 "overviews": my_overview,
#                 "objectives": my_objectives,
#                 "focus_areas": my_focus_area,
#                 "measures": my_measures,
#                 "initiatives": my_initiatives,
                
#                 'grouped_measures': grouped_measures,
#                 'quarterly_data_q1':quarterly_data_q1,
#                 'quarterly_data_q2':quarterly_data_q2,
#                 'quarterly_data_q3':quarterly_data_q3,
#                 'quarterly_data_q4':quarterly_data_q4,
#                 'd1':d1,
#                 'd2':d2,
#                 'd3':d3,
#                 'd4':d4,
#                 'd_objective_names':d_objective_names,

#                 'initiative_status': initiative_status,
#                 'initiative_desc_of_s': initiative_desc_of_s,
#                 'initiative_expected_impact': initiative_expected_impact,
#                 'initiative_notes':initiative_notes,
#     }

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="report.pdf"'

#     template = get_template(template_path)
#     html = template.render(context)

#     pisa_status = pisa.CreatePDF(
#     html, dest=response)

#     if pisa_status.err:
#         return HttpResponse('We had some errors <pre>' + html + '</pre>')
    
           
# Create profile view

    

@login_required(login_url='my-login')
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            first_name = request.user.first_name
            messages.success(request, f'{first_name}, Your profile is updated.')
            return redirect('/')
    else:
        form = ProfileForm(instance=request.user.profile)
    context = {'form':form}
    
    return render(request,'webapp/profile.html', context = context)
        
# Create profile view


@login_required(login_url='my-login')
def approvals(request):
     # Check if any record needs to be approved
    approve_objective = request.GET.get('approve_objective')
    approve_measure = request.GET.get('approve_measure')
    approve_focus_area = request.GET.get('approve_focus_area')
    # print(approve_objective)
    prechecked_objectives = request.session.get('prechecked_objectives', [])
    print(prechecked_objectives)

    # approve
    if approve_objective:
        Objective.objects.filter(pk=int(approve_objective)).update(approved=True)

    if approve_measure:
        Measure.objects.filter(pk=int(approve_measure)).update(approved=True)
        
    if approve_focus_area:
        FocusArea.objects.filter(pk=int(approve_focus_area)).update(approved=True)
 
    if request.method == "POST":
        objectives_id_list = request.POST.getlist('objective_boxes')
        measures_id_list = request.POST.getlist('measure_boxes')
        focus_areas_id_list = request.POST.getlist('focus_area_boxes')
        
        # update the db objectives
        for id in objectives_id_list:
            print(id)
            Objective.objects.filter(pk=int(id)).update(approved=True)
            

        # update the db measures 
        for id in measures_id_list:
            Measure.objects.filter(pk=int(id)).update(approved=True)
        
        # update the db focusareas
        for id in focus_areas_id_list:
            FocusArea.objects.filter(pk=int(id)).update(approved=True)

        # Clear session variables
        if 'prechecked_objectives' in request.session:
            del request.session['prechecked_objectives']
        if 'prechecked_measures' in request.session:
            del request.session['prechecked_measures']
        if 'prechecked_focus_areas' in request.session:
            del request.session['prechecked_focus_areas']

        messages.success(request,("Your approvals were successfully submitted!"))

    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        department_id_fetched = request.GET.get('department_id')
        fiscal_year_id_fetched = request.GET.get('fiscal_year_id')
        
        objectives_pending_approval, focus_areas_pending_approval, measures_pending_approval = get_pending_approvals(department_id_fetched, fiscal_year_id_fetched)
        
        context = {
            'objectives': objectives_pending_approval,
            'focus_areas': focus_areas_pending_approval,
            'measures': measures_pending_approval,
            'prechecked_objectives_json': json.dumps(request.session.get('prechecked_objectives', [])),
            'prechecked_measures_json': json.dumps(request.session.get('prechecked_measures', [])),
            'prechecked_focus_areas_json': json.dumps(request.session.get('prechecked_focus_areas', [])),
            
        }
        
        return JsonResponse(context)
    
    context = {
        'form1': ApprovalsFilterForm(),

    }
    
    return render(request, 'webapp/approvals.html', context=context)


def get_pending_approvals(department_id, fiscal_year_id):
    if department_id and fiscal_year_id:
        objectives_pending_approval = list(Objective.objects.filter(approved=False, department_id=department_id, fiscal_year_id=fiscal_year_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False, department_id=department_id, fiscal_year_id=fiscal_year_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False, department_id=department_id, fiscal_year_id=fiscal_year_id).values('id', 'title', 'objective__name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
    elif department_id:
        objectives_pending_approval = list(Objective.objects.filter(approved=False, department_id=department_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False, department_id=department_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False, department_id=department_id).values('id', 'title', 'objective__name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
    elif fiscal_year_id:
        objectives_pending_approval = list(Objective.objects.filter(approved=False, fiscal_year_id=fiscal_year_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False, fiscal_year_id=fiscal_year_id).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False, fiscal_year_id=fiscal_year_id).values('id', 'title', 'fiscal_year__name', 'objective__name', 'department__name', 'created_at', 'created_by'))
    else:
        objectives_pending_approval = list(Objective.objects.filter(approved=False).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False).values('id', 'name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
        measures_pending_approval = list(Measure.objects.filter(approved=False).values('id', 'title', 'objective__name', 'fiscal_year__name', 'department__name', 'created_at', 'created_by'))
    
    return objectives_pending_approval, focus_areas_pending_approval, measures_pending_approval

    
# @login_required(login_url='my-login')
# def approvals(request):
#     department_id_fetched = request.GET.get('department_id')
#     fiscal_year_id_fetched =  request.GET.get('fiscal_year_id')

    # # Check if any record needs to be approved
    # approve_objective = request.GET.get('approve_objective')
    # approve_measure = request.GET.get('approve_measure')
    # approve_focus_area = request.GET.get('approve_focus_area')
    # print(approve_objective)
    

    # # approve
    # if approve_objective:
    #     Objective.objects.filter(pk=int(approve_objective)).update(approved=True)

    # if approve_measure:
    #     Measure.objects.filter(pk=int(approve_measure)).update(approved=True)
        
    # if approve_focus_area:
    #     FocusArea.objects.filter(pk=int(approve_focus_area)).update(approved=True)

    # # Pass Pre-checked records
    # prechecked_objectives = request.session.get('prechecked_objectives', [])
    # prechecked_measures = request.session.get('prechecked_measures', [])
    # prechecked_focus_areas = request.session.get('prechecked_focus_areas', [])

 
    # if request.method == "POST":
    #     objectives_id_list = request.POST.getlist('objective_boxes')
    #     measures_id_list = request.POST.getlist('measure_boxes')
    #     focus_areas_id_list = request.POST.getlist('focus_area_boxes')
        
    #     # update the db objectives
    #     for id in objectives_id_list:
    #         print(id)
    #         Objective.objects.filter(pk=int(id)).update(approved=True)
            

    #     # update the db measures 
    #     for id in measures_id_list:
    #         Measure.objects.filter(pk=int(id)).update(approved=True)
        
    #     # update the db focusareas
    #     for id in focus_areas_id_list:
    #         FocusArea.objects.filter(pk=int(id)).update(approved=True)

    #     # Clear session variables
    #     if 'prechecked_objectives' in request.session:
    #         del request.session['prechecked_objectives']
    #     if 'prechecked_measures' in request.session:
    #         del request.session['prechecked_measures']
    #     if 'prechecked_focus_areas' in request.session:
    #         del request.session['prechecked_focus_areas']

    #     messages.success(request,("Your approvals were successfully submitted!"))

#     if department_id_fetched and fiscal_year_id_fetched:
#         objectives_pending_approval = Objective.objects.filter(approved=False, department_id=department_id_fetched, fiscal_year_id=fiscal_year_id_fetched)
#         focus_areas_pending_approval = FocusArea.objects.filter(approved=False, department_id=department_id_fetched, fiscal_year_id=fiscal_year_id_fetched)
#         measures_pending_approval = Measure.objects.filter(approved=False, department_id=department_id_fetched, fiscal_year_id=fiscal_year_id_fetched)
#     elif department_id_fetched:
#         # print(department_id_fetched)
#         objectives_pending_approval = Objective.objects.filter(approved=False, department_id=department_id_fetched)
#         focus_areas_pending_approval = FocusArea.objects.filter(approved=False, department_id=department_id_fetched)
#         measures_pending_approval = Measure.objects.filter(approved=False, department_id=department_id_fetched)
#     elif fiscal_year_id_fetched:
#         # print(fiscal_year_id_fetched)
#         objectives_pending_approval = Objective.objects.filter(approved=False, fiscal_year_id=fiscal_year_id_fetched)
#         focus_areas_pending_approval = FocusArea.objects.filter(approved=False, fiscal_year_id=fiscal_year_id_fetched)
#         measures_pending_approval = Measure.objects.filter(approved=False, fiscal_year_id=fiscal_year_id_fetched)
#     else:
#         objectives_pending_approval = Objective.objects.filter(approved=False)
#         focus_areas_pending_approval = FocusArea.objects.filter(approved=False)
#         measures_pending_approval = Measure.objects.filter(approved=False)

#     context = {
#         'form1': ApprovalsFilterForm(),
#         'objectives': objectives_pending_approval,
#         'focus_areas': focus_areas_pending_approval,
#         'measures': measures_pending_approval,
#         'prechecked_data': json.dumps({
#             'prechecked_objectives': prechecked_objectives,
#             'prechecked_measures': prechecked_measures,
#             'prechecked_focus_areas': prechecked_focus_areas,
#         })
#     }

#     return render(request, 'webapp/approvals.html', context=context)
    
    # if department_id_fetched and fiscal_year_id_fetched:
    #     objectives_pending_approval = list(Objective.objects.filter(approved=False, department_id=department_id_fetched, fiscal_year_id=fiscal_year_id_fetched).values('id', 'name', 'fiscal_year__name', 'department__name','created_at','created_by'))
    #     focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False, department_id=department_id_fetched, fiscal_year_id=fiscal_year_id_fetched).values('id', 'name', 'fiscal_year__name','department__name','created_at','created_by'))
    #     measures_pending_approval = list(Measure.objects.filter(approved=False, department_id=department_id_fetched, fiscal_year_id=fiscal_year_id_fetched).values('id', 'title', 'objective__name', 'fiscal_year__name','department__name','created_at','created_by'))
        
    #     context = {
      
    #         'objectives':objectives_pending_approval,
    #         'focus_areas':focus_areas_pending_approval,
    #         'measures':measures_pending_approval,
    #         'prechecked_data':json.dumps({
    #         'prechecked_objectives': prechecked_objectives,
    #         'prechecked_measures': prechecked_measures,
    #         'prechecked_focus_areas': prechecked_focus_areas,
    #         })

    #     }
    #     return JsonResponse(context)
    
    # elif department_id_fetched:
    #      objectives_pending_approval = list(Objective.objects.filter(approved=False, department_id=department_id_fetched).values('id', 'name', 'fiscal_year__name','department__name','created_at','created_by'))
    #      focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False, department_id=department_id_fetched).values('id', 'name', 'fiscal_year__name','department__name','created_at','created_by'))
    #      measures_pending_approval = list(Measure.objects.filter(approved=False, department_id=department_id_fetched).values('id', 'title', 'objective__name', 'fiscal_year__name','department__name','created_at','created_by'))

    #      context = {
      
    #         'objectives':objectives_pending_approval,
    #         'focus_areas':focus_areas_pending_approval,
    #         'measures':measures_pending_approval,
    #         'prechecked_data':json.dumps({
    #         'prechecked_objectives': prechecked_objectives,
    #         'prechecked_measures': prechecked_measures,
    #         'prechecked_focus_areas': prechecked_focus_areas,
    #         })

    #     }
    #      return JsonResponse(context)
    # elif fiscal_year_id_fetched:
    #      objectives_pending_approval = list(Objective.objects.filter(approved=False,  fiscal_year_id=fiscal_year_id_fetched).values('id', 'name', 'fiscal_year__name','department__name','created_at','created_by'))
    #      focus_areas_pending_approval = list(FocusArea.objects.filter(approved=False, fiscal_year_id=fiscal_year_id_fetched).values('id', 'name', 'fiscal_year__name','department__name','created_at','created_by'))
    #      measures_pending_approval = list(Measure.objects.filter(approved=False,  fiscal_year_id=fiscal_year_id_fetched).values('id', 'title', 'fiscal_year__name','objective__name', 'department__name','created_at','created_by'))
      

    #      context = {
      
    #         'objectives':objectives_pending_approval,
    #         'focus_areas':focus_areas_pending_approval,
    #         'measures':measures_pending_approval,
    #         'prechecked_data':json.dumps({
    #         'prechecked_objectives': prechecked_objectives,
    #         'prechecked_measures': prechecked_measures,
    #         'prechecked_focus_areas': prechecked_focus_areas,
    #         })

    #     }
    #      return JsonResponse(context)
    # else:
    
    #     objectives_pending_approval = Objective.objects.filter(approved=False)
    #     focus_areas_pending_approval = FocusArea.objects.filter(approved=False)
    #     measures_pending_approval = Measure.objects.filter(approved=False)

    #     context = {
    #         'form1': ApprovalsFilterForm(),
    #         'objectives':objectives_pending_approval,
    #         'focus_areas':focus_areas_pending_approval,
    #         'measures':measures_pending_approval,
            
    #         'prechecked_objectives': prechecked_objectives,
    #         'prechecked_measures': prechecked_measures,
    #         'prechecked_focus_areas': prechecked_focus_areas,
            
   
    #     }
       
    #     return render(request,'webapp/approvals.html', context = context)
    
    
    
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
        elif item_type == 'focus':
            prechecked_focus_areas = session_data.get('prechecked_focus_areas', [])
            if is_checked:
                prechecked_focus_areas.append(item_id)
            else:
                prechecked_focus_areas.remove(item_id)
            session_data['prechecked_focus_areas'] = prechecked_focus_areas

        # Manually save the session data
        request.session.modified = True

        return JsonResponse({'message': 'Session updated successfully'})


    








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

# View Objective Info
@login_required(login_url='my-login')
def view_measure_info(request,pk):
        
    #  department = Department.objects.get(id=request.user.department_id)
     measure = Measure.objects.get(id=pk)
  
     context = {
        # 'department':department,
        'measure':measure,
        
    } 
    
     return render(request, 'webapp/view-measure-info.html', context=context)


# View Objective Info
@login_required(login_url='my-login')
def view_focus_area_info(request,pk):
        
    #  department = Department.objects.get(id=request.user.department_id)
     focus_area = FocusArea.objects.get(id=pk)
  
     context = {
        # 'department':department,
        'focus_area':focus_area,
        
    } 
    
     return render(request, 'webapp/view-focus-area-info.html', context=context)





# - User logout

def user_logout(request):
    auth.logout(request)
    messages.success(request, "Logout success!")

    return redirect("my-login")

