from django.conf import settings
from django.db import models
from django import forms
from django.contrib.auth.models import User, AbstractUser, UserManager, AbstractBaseUser, PermissionsMixin
from datetime import datetime, date
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

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
    
    name = models.CharField(max_length=100, null=True)   
    description = models.CharField(max_length=100)    
    
    class Meta:
        ordering = ["name"]        
    def __str__(self) -> str:
        return self.name  
    
class CustomerUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(max_length=100, blank='', unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True, default='')
    last_name = models.CharField(max_length=100, null=True, blank=True, default='')
  
    
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)  
     
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    is_dept_head = models.BooleanField(default=False)
    is_citymanager_office = models.BooleanField(default=False)
    
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
        return self.first_name + self.last_name

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


 
 
    
             
class Objective(TimeStampMixin):
    name = models.TextField(max_length=255)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)   
    def __str__(self) -> str:
        return self.name 

class FocusArea(TimeStampMixin):
    name = models.TextField(max_length=255)
    department = models.ForeignKey("Department", on_delete=models.CASCADE) 
    def __str__(self) -> str:
        return self.name     
 
class Overview(TimeStampMixin):
    name = models.TextField(max_length=800)
    department = models.ForeignKey("Department", on_delete=models.CASCADE) 
    def __str__(self) -> str:
        return self.name  
         
class Mission(TimeStampMixin):
    name = models.TextField(max_length=800, null=True)   
    
    department = models.ForeignKey("Department", on_delete=models.CASCADE, related_name='missions')
      
    class Meta:
        ordering = ["name"]
        
    def __str__(self) -> str:
        return self.name   


PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]  
 
class Measure(TimeStampMixin):
    
    objective = models.ForeignKey("Objective", on_delete=models.CASCADE)   
    title = models.TextField(max_length=500)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)   
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
    
    # previous_year_rate = models.DecimalField(max_digits=3, decimal_places=0, default=Decimal(0), validators=PERCENTAGE_VALIDATOR)
    
    current_year_rate = models.DecimalField(max_digits=3, decimal_places=0, default=Decimal(0), validators=PERCENTAGE_VALIDATOR)
    target_rate = models.DecimalField(max_digits=3, decimal_places=0, default=Decimal(0), validators=PERCENTAGE_VALIDATOR)
    
    
    def __str__(self) -> str:
        return self.title

class QuarterlyPerformanceData(TimeStampMixin):
    
    objective = models.ForeignKey("Objective", on_delete=models.CASCADE)       
    department = models.ForeignKey("Department", on_delete=models.CASCADE) 
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
        quarter = self.quarter
        if self.quarter == 'Q1':
            percentage = (self.numerator / self.denominator) * 100
        return percentage
    
    
        
class StrategicInitiative(TimeStampMixin):
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    title = models.TextField(max_length=255)
    description = models.TextField(max_length=255, null=True, blank=True)
    proposed_completion_date = models.DateField(auto_now=True)
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
        ("High Impact", "Hign Impact"),
    ) 
    expected_impact = models.TextField(max_length=255, choices=IMPACT_CHOICES, null=True, blank=True) # Impact of Initiative 
    
    description_project_status = models.CharField(max_length=255) # Describe milestones achieved during the quarter. 
    
    notes = models.TextField(max_length=255, null=True, blank=True)
    def __str__(self) -> str:
        return self.title 
    
class StrategicInitiativeDetail(TimeStampMixin):
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    strategic_initiative = models.ForeignKey("StrategicInitiative", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    