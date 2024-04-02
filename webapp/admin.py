from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin
from .custom_user_admin import UserAdmin

from . models import *

# admin.site.register(CustomerUser) # no longer need it as it's already had a customer_user_admin.py

SITE_TITLE = "City of Rocky Mount Performance Measurement Admin"
admin.site.site_header = SITE_TITLE
admin.site.site_title = SITE_TITLE


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at',)
    fields = (
        # 'id',
        'name',
        'description',
    )    
admin.site.register(Department, DepartmentAdmin)

class MissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at',)
    fields = (
        # 'id',
        'name',
        'department',
    ) 
admin.site.register(Mission, MissionAdmin)

class OverviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at',)
    fields = (
        # 'id',
        'name',
        'department',
    ) 
admin.site.register(Overview, OverviewAdmin)

class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at',)
    fields = (
        # 'id',
        'name',
        'department',
    ) 
    
admin.site.register(Objective, ObjectiveAdmin)

class FocusAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'name', 'created_at',)
    fields = (
        # 'id',
        'name',
        'department',
    ) 
admin.site.register(FocusArea, FocusAreaAdmin)

class MeasureAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'objective_id', 'title', 'direction', 'frequency', 'current_year_rate','target_rate','created_at',)
    fields = (
        # 'id',
        'title',
        'department',
    ) 
admin.site.register(Measure, MeasureAdmin)


class StrategicInitiativeAdmin(admin.ModelAdmin):
    list_display = ('id', 'department', 'title',  'proposed_completion_date',  'created_at',)
    fields = (
        # 'id',
        'title',
        'department',

    ) 
admin.site.register(StrategicInitiative, StrategicInitiativeAdmin)

admin.site.register(QuarterlyPerformanceData)



