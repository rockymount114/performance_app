from django.conf import settings
from django.db import models

from django import forms
from django.contrib.auth.models import User, AbstractUser, UserManager, AbstractBaseUser, PermissionsMixin
from datetime import datetime, date
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import datetime
# from .validators import PhoneNumberField  
from django.core.validators import RegexValidator



class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# manage User model
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)



class Department(TimeStampMixin): 
    
    name = models.CharField(max_length=100)   
    description = models.CharField(max_length=100, null=True, blank=True)    
    extension_granted_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["name"]        
    def __str__(self) -> str:
        return self.name  
    
class CustomerUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(max_length=100, blank='', unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True, default='')
    last_name = models.CharField(max_length=100, null=True, blank=True, default='')
  
    
    department = models.ForeignKey(Department, null=True, on_delete=models.CASCADE)  
     
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    is_manager = models.BooleanField(default=False) # can input data
    is_dept_head = models.BooleanField(default=False)
    is_citymanager_office = models.BooleanField(default=False)
    accessible_departments = models.ManyToManyField(Department, related_name='accessible_to_users', blank=True)
    is_global_performance_officer = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'CustomerUser'
        verbose_name_plural = 'CustomerUsers'
        
              
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    @property
    def get_user_role(self):
        if self.is_superuser:
            role = "Admin"
        elif self.is_dept_head:
            role = "Department Head"
        elif self.is_citymanager_office:
            role = "City Manager Officer"

    @property
    def get_head_name(self):
        if self.is_dept_head:
            full_name = f"{self.first_name} {self.last_name}"
            return full_name.strip()
    @property
    def get_head_email(self):
        if self.is_dept_head:
            return self.email
        
 
#  Fiscal Year Model
class FiscalYear(TimeStampMixin):
    name = models.CharField(max_length=6) 

    def __str__(self) -> str:
        return self.name  

class Mission(TimeStampMixin):
    name = models.TextField(max_length=800, null=True)   
    department = models.ForeignKey("Department", on_delete=models.CASCADE, related_name='missions')
    # fiscal_year = models.ForeignKey("FiscalYear", on_delete=models.CASCADE)
      
    class Meta:
        ordering = ["name"]
        
    def __str__(self) -> str:
        return self.name  
         
class Overview(TimeStampMixin):
    name = models.TextField(max_length=800)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    # fiscal_year = models.ForeignKey("FiscalYear", on_delete=models.CASCADE) 
    def __str__(self) -> str:
        return self.name  
         
              
class Objective(TimeStampMixin):
    name = models.TextField(max_length=500)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)   
    approved = models.BooleanField('Approved',default = False)
    fiscal_year = models.ForeignKey("FiscalYear", on_delete=models.CASCADE)  
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)
    focus_area = models.ManyToManyField("FocusArea")

    def __str__(self) -> str:
        return self.name 

class FocusArea(TimeStampMixin):
    name = models.TextField(max_length=255)
    # department = models.ForeignKey("Department", on_delete=models.CASCADE) 
    # approved = models.BooleanField('Approved',default=False)
    # fiscal_year = models.ForeignKey("FiscalYear", on_delete=models.CASCADE)
    description = models.TextField(max_length=300, null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return self.name     
 
  


PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]  
 
class Measure(TimeStampMixin):
    
    objective = models.ForeignKey("Objective", on_delete=models.CASCADE)   
    title = models.TextField(max_length=500)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)  
    approved = models.BooleanField('Approved',default=False) 
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)
    
    DIRECTIONS = (
        ("Upwards", "Upwards"),
        ("Downwards", "Downwards"),
    )  
    
    direction = models.CharField(max_length=255, choices= DIRECTIONS, default="Upwards") 
    
    FREQUENCY_CHOICES = (
        ("Quarterly", "Quarterly"),
        ("Annually", "Annually"),
    )    
    frequency = models.CharField(max_length=255, choices= FREQUENCY_CHOICES, default="Quarterly")    
    
    current_year_rate = models.DecimalField(max_digits=3, decimal_places=0, default=Decimal(0), validators=PERCENTAGE_VALIDATOR)
    
    NUMBER_CHOICES = (
        (True, "Number"),
        (False, "Rate"),
    ) 
    
    is_number = models.BooleanField(default=False, choices= NUMBER_CHOICES)
    
    target_number = models.IntegerField(null=True, blank=True, default=0)
    target_rate = models.DecimalField(max_digits=3, decimal_places=0, default=Decimal(0), validators=PERCENTAGE_VALIDATOR, null=True, blank=True)
    
    fiscal_year = models.ForeignKey("FiscalYear", on_delete=models.CASCADE)
    
    
    
    def __str__(self) -> str:
        return self.title

class QuarterlyPerformanceData(TimeStampMixin):
    
    objective = models.ForeignKey("Objective", on_delete=models.CASCADE)       
    department = models.ForeignKey("Department", on_delete=models.CASCADE) 
    measure = models.ForeignKey("Measure", on_delete=models.CASCADE) 
    
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)
    
    QUARTER_CHOICES = (
        ("Q1", "Q1"),
        ("Q2", "Q2"),
        ("Q3", "Q3"),
        ("Q4", "Q4"),
    ) 
    
    quarter = models.CharField(max_length=100, null=True, choices= QUARTER_CHOICES)
    
    numerator = models.IntegerField(null=True)              # total job actual done within this quarter
    denominator = models.IntegerField(null=True, default=5) # total target job number within this quarter
    # value
    # numerical_value
    IMPACT_CHOICES = (
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("Moderate", "Moderate"),
        ("High Impact", "Hign Impact"),
    ) 
    
    impact = models.CharField(max_length=100, null=True, choices= IMPACT_CHOICES)
    descriptive_impact = models.TextField(max_length=500, null=True, blank=True) 
   
    def __str__(self) -> str:
        return str(self.quarter)
    
    @property
    def get_percentage(self):
        
        
        percentage = f"{int((self.numerator / self.denominator) * 100)} % "
        return percentage
    
    @property        
    def get_percentage_int(self):
        
        
        percentage = int((self.numerator / self.denominator) * 100)
        return percentage
    @property
    def get_annual_percentage(self):
        quarter = self.quarter
        if self.quarter == quarter:
            percentage = f"{int((self.numerator / self.denominator) * 100)} % "
        return percentage
    

    
    
class StrategicInitiative(TimeStampMixin):
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    title = models.TextField(max_length=500)
    description = models.TextField(max_length=1000, null=True, blank=True)
    proposed_completion_date = models.DateField()
    fiscal_year = models.ForeignKey("FiscalYear", on_delete=models.CASCADE)
    
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return self.title 
    
class StrategicInitiativeDetail(TimeStampMixin):
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    strategic_initiative = models.ForeignKey("StrategicInitiative", on_delete=models.CASCADE)
    
    created_by = models.CharField(max_length=50, null=True)
    modified_by = models.CharField(max_length=50, null=True)
    
    STATUS_CHOICES = (
        ("0-25%", "0-25%"),
        ("25-50%", "25-50%"),
        ("50-75%", "50-75%"),
        ("75-99%", "75-99%"),
        ("Completed", "Completed"),
    ) 
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, null=True, blank=True)
    IMPACT_CHOICES = (
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("Moderate", "Moderate"),
        ("High Impact", "High Impact"),
    ) 
    expected_impact = models.TextField(max_length=255, choices=IMPACT_CHOICES, null=True, blank=True) # Impact of Initiative 
    
    description_project_status = models.CharField(max_length=255) # Describe milestones achieved during the quarter. 
    
    notes = models.TextField(max_length=255, null=True, blank=True)
    




class Profile(models.Model):
    user = models.OneToOneField(CustomerUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True, blank=True)
    work_phone = models.CharField(
        max_length=12,
        validators=[RegexValidator(
            regex=r'^\d{3}-\d{3}-\d{4}$',
            message='Work phone number must be entered in the format: xxx-xxx-xxxx.'
        )],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"