from email.headerregistry import ContentTypeHeader
from django.contrib.auth.models import Group, Permission

from .models import Measure


department_heads_group = Group.objects.create(name='Department Heads')
city_managers_group = Group.objects.create(name='City Managers')


view_performance_permission = Permission.objects.create(codename='view_performance',
                                                        name='Can view performance data',
                                                        content_type=ContentTypeHeader.objects.get_for_model(Measure))


department_heads_group.permissions.add(view_performance_permission)

city_managers_group.permissions.add(view_performance_permission)