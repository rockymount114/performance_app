from typing import Any, Mapping
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth.models import User
from django.forms import ClearableFileInput
from .models import Profile
from django.forms import ModelForm
from django.forms.widgets import FileInput

from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.forms import DateInput
from .models import *
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from django.core.validators import RegexValidator
# from .views import get_current_fiscal_year
import re

from .changes_utils import *

User = get_user_model()


def get_current_fiscal_year():                
    current_month = date.today().month        
    if current_month >= 7:
        fiscal_year = f'FY{date.today().year + 1}'
    else:
        fiscal_year = f'FY{date.today().year}'     
    
    return fiscal_year  

# - Register/Create a user

class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomerUser
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name']

    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].error_messages['required'] = 'First name is required'
        self.fields['last_name'].error_messages['required'] = 'Last name is required'
        self.fields['first_name'].help_text = 'Please enter your first name'
        self.fields['last_name'].help_text = 'Please enter your last name'

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if not first_name:
            self.add_error('first_name', 'First name is required.')

        if not last_name:
            self.add_error('last_name', 'Last name is required.')

        return cleaned_data
    
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if not re.match(r'^[\w\.-]+@rockymountnc\.gov$', email):
    #         raise ValidationError('Email must be ending with @rockymountnc.gov')
    #     return email

# - Login a user

class LoginForm(forms.Form):
    # username = forms.CharField(widget=TextInput())
    email = forms.EmailField(label="Email", max_length=100)
    password = forms.CharField(widget=PasswordInput())

# for superuser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomerUser
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        return self.cleaned_data['email']

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomerUser
        fields = ('email', 'first_name', 'last_name', 'department')

    def clean_email(self):
        return self.cleaned_data['email']
    
# - Create a measure

# class CreateMeasureForm(forms.ModelForm):
#     title = forms.CharField(
#         widget=forms.Textarea(attrs={'placeholder': 'Please input Your Measure Metrics here, max 200 characters'}),
#         label="Metric name",
#         max_length=255,
#         required=False,
#     )

#     department = forms.ModelChoiceField(
#         queryset=Department.objects.all(),
#         disabled=True,
#         required=False,
#     )

#     fiscal_year = forms.ModelChoiceField(
#         queryset=FiscalYear.objects.all(),
#         disabled=True,
#         required=False,
    
#     )


#     class Meta:
#         model = Measure
#         # fields = '__all__'
        
#         fields = ['objective','title','fiscal_year', 'direction', 'frequency', 'current_year_rate', 'target_rate']  
#         exclude = ['department', 'created_by']



class CreateMeasureForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Measure Metrics here, max 500 characters'}),
        label="Metric name",
        max_length=500,
        required=True,
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,
    )
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        department_id = kwargs.pop('department_id', None)
        fiscal_year_id = kwargs.pop('fiscal_year_id', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_global_performance_officer or user.is_citymanager_office or user.is_dept_head:
                # For users with elevated access, use the department from the dropdown
                self.fields['department'].initial = department_id if department_id else user.department_id
            else:
                # For regular users, use their assigned department
                self.fields['department'].initial = user.department_id

            # Use the fiscal year from the dropdown if provided, otherwise use the current fiscal year
            if fiscal_year_id:
                self.fields['fiscal_year'].initial = fiscal_year_id
            else:
                current_fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())
                self.fields['fiscal_year'].initial = current_fiscal_year.id

            self.fields['objective'].queryset = Objective.objects.filter(
                department_id=self.fields['department'].initial,
                fiscal_year_id=self.fields['fiscal_year'].initial,
                approved=True
            )

    class Meta:
        model = Measure
        fields = ['objective', 'title', 'fiscal_year', 'direction', 'frequency', 'is_number', 'target_rate', 'target_number']
        exclude = ['department', 'created_by', 'current_year_rate']


# class CreateQuarterlyMeasureForm(forms.ModelForm):
#     class Meta:
#         model = QuarterlyPerformanceData    
#         fields = '__all__' 



class CreateInitiativeForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Initiative here, max 500 characters'}),
        label="Initiative name",
        max_length=500,
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Initiative description here, max 1000 characters'}),
        label="Description",
        max_length=1000,
        required=True,
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,
    )
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=False,
    )
    proposed_completion_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        department_id = kwargs.pop('department_id', None)
        fiscal_year_id = kwargs.pop('fiscal_year_id', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_global_performance_officer or user.is_citymanager_office or user.is_dept_head:
                # For users with elevated access, use the department from the dropdown
                self.fields['department'].initial = department_id if department_id else user.department_id
            else:
                # For regular users, use their assigned department
                self.fields['department'].initial = user.department_id

            # Use the fiscal year from the dropdown if provided, otherwise use the current fiscal year
            if fiscal_year_id:
                self.fields['fiscal_year'].initial = fiscal_year_id
            else:
                current_fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())
                self.fields['fiscal_year'].initial = current_fiscal_year.id

    class Meta:
        model = StrategicInitiative
        fields = ['title', 'description', 'fiscal_year', 'proposed_completion_date']
        exclude = ['department', 'created_by']


class CreateMissionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Mission text here, max 800 characters'}),
        max_length=800,
        required=False,
    )


    class Meta:
        model = Mission
        fields = ['name', ]
      

class CreateOverviewForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Overview text here, max 800 characters'}),
        # label="Please input Overview text here",
        max_length=800,
        required=False,
    )


    class Meta:
        model = Overview    
        fields = ['name']  
        exclude = ['department']


class CreateObjectiveForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Objectives text here, max 500 characters'}),
        label='Objective title',
        max_length=500,
        required=True,

    )

    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=True,
    
    )
    
    focus_area = forms.ModelMultipleChoiceField(
        queryset=FocusArea.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
    
    )
    
    class Meta:
        model = Objective    

        # fields= "__all__"

        fields = ['name', 'fiscal_year', "focus_area"]  
        exclude = ['department', 'approved', 'created_by', 'modified_by']
         
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['fiscal_year'].queryset = FiscalYear.objects.get(name=get_current_fiscal_year()) 
 
class CreateFocusAreaForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Focus Area text here, max 500 characters'}),
        label='Focus Areas',
        max_length=500,
        required=False,
    )

    class Meta:
        model = FocusArea  
        fields = ['name', 'description']
                   
class CreateQuarterlyPerformanceDataForm(forms.ModelForm):

    objective = forms.ModelChoiceField(
        queryset=Objective.objects.all(),
        disabled=True,
        required=False,
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,
    )

    measure = forms.ModelChoiceField(
        queryset=Measure.objects.all(),
        disabled=True,
        required=False,
    )

    quarter = forms.ChoiceField(
        choices=QuarterlyPerformanceData.QUARTER_CHOICES,
        disabled=True,
        required=False,
    )
    


    class Meta:
        model =  QuarterlyPerformanceData  
        fields = ['numerator','denominator','impact','descriptive_impact']
        exclude = ['department','objective','measure', 'quarter']
        
# this filter is for dashboard.html filter out department & fiscal year if you login as CMO
    
class DepartmentFilterForm(forms.Form):
    departments = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=False,
        required=True,
    )
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=False,
        required=True,
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            if user.is_global_performance_officer:
                self.fields['departments'].queryset = Department.objects.all()
            elif user.accessible_departments.exists():
                self.fields['departments'].queryset = user.accessible_departments.all()
     

# This is a test form to filter pending approvals dynamically based on Departmnet and fiscal year
    
class ApprovalsFilterForm(forms.Form):
    departments = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=False,
        required=True,
    )
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=False,
        required=True,
        initial=FiscalYear.objects.get(name=get_current_fiscal_year()),  # Your function to get the current fiscal year
        widget=forms.Select(attrs={'onchange': 'filterResults(this.value)'}),
    )
        
  
        
class StrategicInitiativeDetailForm(forms.ModelForm):

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,
    )

    strategic_initiative = forms.ModelChoiceField(
        queryset=StrategicInitiative.objects.all(),
        disabled=True,
        required=False,
    )

    class Meta:
        model =  StrategicInitiativeDetail  
        fields = ['status','expected_impact','description_project_status','notes']
        exclude = ['department','strategic_initiative']


# UPDATE FORMS
#  - Update Measures
class UpdateMeasureForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Measure Metrics here, max 500 characters'}),
        label="Metric name",
        max_length=500,
        required=True,
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,
    )
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=False,
    )
    is_number = forms.ChoiceField(
        choices=((True, 'Yes'), (False, 'No')),
        label="Is this measure a number?",
        widget=forms.Select(),
        required=True
    )
    target_number = forms.IntegerField(required=False)
    target_rate = forms.DecimalField(max_digits=3, decimal_places=0, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        department_id = kwargs.pop('department_id', None)
        fiscal_year_id = kwargs.pop('fiscal_year_id', None)
        super().__init__(*args, **kwargs)
        
        if self.instance:
            self.fields['is_number'].initial = 'True' if self.instance.is_number else 'False'
            if self.instance.is_number:
                self.fields['target_number'].initial = self.instance.target_number
            else:
                self.fields['target_rate'].initial = self.instance.target_rate

        if user:
            if user.is_global_performance_officer or user.is_citymanager_office or user.is_dept_head:
                # For users with elevated access, use the department and fiscal year from the dropdown
                if department_id:
                    self.fields['department'].initial = department_id
                else:
                    # If no department_id is provided, use the measure's original department
                    self.fields['department'].initial = self.instance.department_id

                if fiscal_year_id:
                    self.fields['fiscal_year'].initial = fiscal_year_id
                else:
                    # If no fiscal_year_id is provided, use the measure's original fiscal year
                    self.fields['fiscal_year'].initial = self.instance.fiscal_year_id
            else:
                # For regular users, use their assigned department and the measure's original fiscal year
                self.fields['department'].initial = user.department_id
                self.fields['fiscal_year'].initial = self.instance.fiscal_year_id

            self.fields['objective'].queryset = Objective.objects.filter(
                department_id=self.fields['department'].initial,
                fiscal_year_id=self.fields['fiscal_year'].initial,
                approved=True
            )

    def clean_is_number(self):
        # Convert string back to boolean
        return self.cleaned_data['is_number'] == 'True'

    def clean(self):
        cleaned_data = super().clean()
        is_number = cleaned_data.get('is_number')
        target_number = cleaned_data.get('target_number')
        target_rate = cleaned_data.get('target_rate')

        if is_number and target_number is None:
            self.add_error('target_number', 'This field is required when the measure is a number.')
        elif not is_number and target_rate is None:
            self.add_error('target_rate', 'This field is required when the measure is a rate.')

        return cleaned_data
    

    def save(self, commit=True):
        old_instance = Measure.objects.get(pk=self.instance.pk)
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
        
        changes = get_changes(old_instance, instance)
        instance.changes = changes
        return instance

    class Meta:
        model = Measure
        fields = ['department', 'objective', 'title', 'fiscal_year', 'direction', 'frequency', 'is_number', 'target_rate', 'target_number']
        exclude = ['created_by', 'current_year_rate']

# -Update Objectives
class UpdateObjectiveForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Objectives text here, max 500 characters'}),
        label='Objective title',
        max_length=500,
        required=True,

    )

    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=True,
    
    )
    
    focus_area = forms.ModelMultipleChoiceField(
        queryset=FocusArea.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
    
    )

    def save(self, commit=True):
        old_instance = Objective.objects.get(pk=self.instance.pk)
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            self.save_m2m()
        
        changes = get_changes(old_instance, instance)
        
        # Handle ManyToMany fields separately
        old_focus_areas = set(old_instance.focus_area.all())
        new_focus_areas = set(self.cleaned_data['focus_area'])
        if old_focus_areas != new_focus_areas:
            changes['focus_area'] = {
                'old': ', '.join(str(fa) for fa in old_focus_areas),
                'new': ', '.join(str(fa) for fa in new_focus_areas)
            }
        
        instance.changes = changes
        return instance
    
    class Meta:
        model = Objective    


        fields = ['name', 'fiscal_year', "focus_area"]  
        exclude = ['department', 'approved', 'created_by']


# -Update Initiatives 

class UpdateInitiativeForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Initiative here, max 500 characters'}),
        label="Please input Initiative here",
        max_length=500,
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Initiative description here, max 1000 characters'}),
        label="Description",
        max_length=1000,
        required=False,
    )
    
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=True,
    )
    proposed_completion_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )

    class Meta:
        model = StrategicInitiative    
        fields = ['fiscal_year', 'title', 'description', 'proposed_completion_date']  
        exclude = ['department', 'created_by', 'modified_by']


class ExtensionRequestForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,  # Changed to False since we're setting it in the view
    )

    class Meta:
        model = ExtensionRequest
        fields = ['department', 'requested_duration', 'reason']
        widgets = {
            'requested_duration': forms.Select(choices=[
                (1, '1 day'),
                (2, '2 days'),
                (3, '3 days'),
                (4, '4 days'),
                (5, '5 days'),
                (6, '6 days'),
                (7, '7 days'),
            ]),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'requested_duration': 'Please select how many extension days you need',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].widget.attrs['readonly'] = True




# RegexValidator for phone number

phone_number_regex = RegexValidator(
    regex=r'^\d{3}-\d{3}-\d{4}$',
    message="Phone number must be entered in the format: '###-###-####'."
)

class PhoneNumberField(models.CharField):
    default_validators = [phone_number_regex]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = re.sub(r'[\(\)\-\s+]', '', str(value))
        if len(value) == 10:
            return f"{value[:3]}-{value[3:6]}-{value[6:]}"
        return value



class UserUpdateForm(forms.ModelForm):   
    
    class Meta:
        model = CustomerUser
        fields = ['first_name', 'last_name', 'email', 'department']
        read_only_fields = ('department', 'email',)
    
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['department'].disabled = True
        self.fields['email'].disabled = True
       
class ProfileUpdateForm(forms.ModelForm):
    work_phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Phone number format as xxx-xxx-xxxx'}),
        max_length=12,
        validators=[RegexValidator(
            regex=r'^\d{3}-\d{3}-\d{4}$',
            message='Work phone number must be entered in this format: xxx-xxx-xxxx.'
        )],
        required=False
        
    )
    image = forms.ImageField(label='', required=False)
    
    class Meta:
        model = Profile
        fields = ['image', 'work_phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = ''  # Set the label to an empty string
        self.fields['image'].widget = CustomClearableFileInput()  # Use custom widget
        
    def clean_work_phone(self):
        work_phone = self.cleaned_data.get('work_phone')
        if work_phone:
            pattern = r'^\d{3}-\d{3}-\d{4}$'
            import re
            if not re.match(pattern, work_phone):
                raise forms.ValidationError('Work phone number must be in the format: xxx-xxx-xxxx.')
        return work_phone
    
    def clean(self):
        cleaned_data = super().clean()
        self.clean_work_phone()  # Call the clean_work_phone method here
        return cleaned_data

# hide image tags    
class CustomClearableFileInput(ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        html = html.replace('<label', '<label style="display:none;"')
        html = html.replace('Currently: ', '')
        html = html.replace('Clear:', '')
        html = html.replace('Change:', '')
        html = html.replace('<a href=', '<a style="display:none;" href=')
        html = html.replace('<input type="checkbox" name="image-clear" id="image-clear_id">', '')
        return html