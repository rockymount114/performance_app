from typing import Any, Mapping
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth.models import User

from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList

from .models import *
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils import timezone

from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

User = get_user_model()

# - Register/Create a user

class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomerUser
        fields = ['email', 'password1', 'password2']



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

class CreateMeasureForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Please input Your Measure title here, max 200 characters'}),
        max_length=255,
        required=False,
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        disabled=True,
        required=False,
    )

    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=False,
        required=True,
    )


    class Meta:
        model = Measure
        fields = '__all__'



class CreateQuarterlyMeasureForm(forms.ModelForm):
    class Meta:
        model = QuarterlyPerformanceData    
        fields = '__all__' 

class CreateInitiativeForm(forms.ModelForm):

    class Meta:
        model =  StrategicInitiative  
        fields = '__all__'  
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].disabled = True


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
        required=False,

    )

    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.all(),
        disabled=True,
        required=True,
    
    )

    class Meta:
        model = Objective    


        fields = ['name', 'fiscal_year' ]  
        exclude = ['department', 'approved']
         
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].queryset = FiscalYear.objects.order_by('name')   
                
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
        fields = '__all__' 
        
        
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
        fields = '__all__' 

