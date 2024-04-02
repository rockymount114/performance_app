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

User = get_user_model()

# - Register/Create a user

class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomerUser
        fields = ['email', 'password1', 'password2']



# - Login a user

class LoginForm(forms.Form):
    # username = forms.CharField(widget=TextInput())
    email = forms.EmailField(label="email", max_length=100)
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

    class Meta:
        model = Measure    
        fields = '__all__'    
#         # fields = ['site', 'location', 'owner', 'retention', 'content']

class CreateQuarterlyMeasureForm(forms.ModelForm):
    class Meta:
        model = QuarterlyPerformanceData    
        fields = ['objective', 
                  'department', 
                  'quarter', 
                  'numerator', 
                  'denominator', 
                  'impact', 
                  'descriptive_impact' 
                    
                 ]
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable the 'objective' field
        self.fields['objective'].disabled = True

        # Disable the 'department' field
        self.fields['department'].disabled = True

        # Disable the 'quarter' field
        self.fields['quarter'].disabled = True

class CreateInitiativeForm(forms.ModelForm):

    class Meta:
        model =  StrategicInitiative  
        fields = '__all__'    
#         # fields = ['site', 'location', 'owner', 'retention', 'content']


class CreateMissionForm(forms.ModelForm):

    class Meta:
        model = Mission    
        fields = '__all__' 
        name = forms.CharField(label="Wiki title", required=False,
                           widget= forms.TextInput
                           (attrs={
                               'class': 'wiki-title',
                               'name': 'WikiTitle',
                               'placeholder':'Enter Wiki title',
                               'required': 'True'
                            }))

class CreateQuarterlyPerformanceDataForm(forms.ModelForm):

    class Meta:
        model =  QuarterlyPerformanceData  
        fields = ['objective', 
                  'department', 
                  'quarter', 
                  'numerator', 
                  'denominator', 
                  'impact', 
                  'descriptive_impact' 
                    
                 ]
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable the 'objective' field
        self.fields['objective'].disabled = True

        # Disable the 'department' field
        self.fields['department'].disabled = True

        # Disable the 'quarter' field
        self.fields['quarter'].disabled = True 
