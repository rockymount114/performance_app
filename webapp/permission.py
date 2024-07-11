from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Measure

# Create the permission first
view_performance_permission = Permission.objects.create(
    codename='view_performance',
    name='Can view performance data',
    content_type=ContentType.objects.get_for_model(Measure)
)

# Then create groups and add the permission
department_heads_group = Group.objects.create(name='Department Heads')
city_managers_group = Group.objects.create(name='City Managers')
performance_officers_group = Group.objects.get_or_create(name='Performance Officers')[0]

department_heads_group.permissions.add(view_performance_permission)
city_managers_group.permissions.add(view_performance_permission)
performance_officers_group.permissions.add(view_performance_permission)