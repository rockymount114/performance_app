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
from crispy_forms.layout import Layout, Field

from django.core.validators import RegexValidator
# from .views import get_current_fiscal_year
import re

User = get_user_model()


def get_current_fiscal_year():                
    current_month = date.today().month        
    if current_month > 7:
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
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Measure Metrics here, max 200 characters'}),
        label="Metric name",
        max_length=255,
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
        super().__init__(*args, **kwargs)
        if user:
            department_id = user.department_id
            current_fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())
            self.fields['objective'].queryset = Objective.objects.filter(
                department_id=department_id,
                fiscal_year=current_fiscal_year,
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
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Initiative here, max 255 characters'}),
        label="Please input Initative here",
        max_length=255,
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Initiative description here, max 1000 characters'}),
        label="Description",
        max_length=1000,
        required=True,
    )
    
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=False,
        required=True,
    )
    proposed_completion_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False,
    )

    class Meta:
        model = StrategicInitiative    
        fields = ['title','description','proposed_completion_date']  
        exclude = ['department']


class CreateMissionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Mission text here, max 800 characters'}),
        max_length=800,
        required=False,
    )

    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=False,
        required=True,
    )

    class Meta:
        model = Mission    
        # fields = "__all__"
        fields = ['name']  
        exclude = ['department']  

class CreateOverviewForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Overview text here, max 800 characters'}),
        # label="Please input Overview text here",
        max_length=800,
        required=False,
    )

    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=False,
        required=True,
    )

    class Meta:
        model = Overview    
        fields = ['name']  
        exclude = ['department']


class CreateObjectiveForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Objectives text here, max 300 characters'}),
        label='Objective title',
        max_length=300,
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
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Focus Area text here, max 300 characters'}),
        label='Focus Areas',
        max_length=300,
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
        initial=get_current_fiscal_year(),  # Your function to get the current fiscal year
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
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Measure Metrics here, max 200 characters'}),
        label="Metric name",
        max_length=255,
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
        super().__init__(*args, **kwargs)
        if user:
            department_id = user.department_id
            current_fiscal_year = FiscalYear.objects.get(name=get_current_fiscal_year())
            self.fields['objective'].queryset = Objective.objects.filter(
                department_id=department_id,
                fiscal_year=current_fiscal_year,
                approved=True
            )

    class Meta:
        model = Measure
        fields = ['department','objective', 'title', 'fiscal_year', 'direction', 'frequency', 'is_number', 'target_rate', 'target_number']
        exclude = [ 'created_by', 'current_year_rate']

# -Update Objectives
class UpdateObjectiveForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Department Objectives text here, max 300 characters'}),
        label='Objective title',
        max_length=300,
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


        fields = ['name', 'fiscal_year', "focus_area"]  
        exclude = ['department', 'approved', 'created_by']




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