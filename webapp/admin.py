from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin
from .custom_user_admin import UserAdmin

from . models import *

# admin.site.register(CustomerUser) # no longer need it as it's already had a customer_user_admin.py

SITE_TITLE = "City of Rocky Mount Performance Management Tracker Admin"
admin.site.site_header = SITE_TITLE
admin.site.site_title = SITE_TITLE


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'has_active_extension', 'extension_deadline')
    search_fields = ('name', 'description')

@admin.register(ExtensionRequest)
class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ('department', 'requested_by', 'requested_at', 'requested_duration', 'status')
    list_filter = ('status', 'requested_at')
    search_fields = ('department__name', 'requested_by__username', 'reason')

@admin.register(ExtensionLog)
class ExtensionLogAdmin(admin.ModelAdmin):
    list_display = ('department', 'granted_by', 'granted_at', 'duration')
    list_filter = ('granted_at',)
    search_fields = ('department__name', 'granted_by__username', 'reason')

class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at',)
    fields = (
       
        'name',
   

    ) 
    
admin.site.register(FiscalYear, FiscalYearAdmin)

class MissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at',)
    fields = (
        # 'id',
        'department',
        'name',
      
        
    ) 
admin.site.register(Mission, MissionAdmin)

class OverviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at',)
    fields = (
     
        'department',
        'name',
        
    ) 
admin.site.register(Overview, OverviewAdmin)

class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at', 'approved','fiscal_year',)
    fields = (
       
        'fiscal_year',
        'department',
        'name',
        'focus_area',
        'approved'

    ) 
    
admin.site.register(Objective, ObjectiveAdmin)

class FocusAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at',)
    fields = (
 
        'name',
        'description',
     
    ) 
    
    
admin.site.register(FocusArea, FocusAreaAdmin)

class MeasureAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'title','objective', 'title', 'direction', 'frequency', 'current_year_rate','target_rate','created_at',)
    fields = (
        
        'fiscal_year',
        'department',
        'objective',
        'title',
        'direction',
        'frequency',
        'is_number',
        'target_number',
        'target_rate',
       
    ) 
admin.site.register(Measure, MeasureAdmin)


class StrategicInitiativeAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'title',  'description','proposed_completion_date',  'created_at',)
    fields = (
        # 'id',
        'fiscal_year',
        'department',
        'title',
        'description',
        'proposed_completion_date',

    ) 
admin.site.register(StrategicInitiative, StrategicInitiativeAdmin)

admin.site.register(QuarterlyPerformanceData)
admin.site.register(StrategicInitiativeDetail)

admin.site.register(Profile)



