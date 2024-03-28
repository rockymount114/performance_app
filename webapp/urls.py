
from django.urls import path
from django.conf.urls import (handler404)
from . import views

handler404 = 'webapp.views.handler404'

urlpatterns = [

    path('', views.home, name=""),

    path('register', views.register, name="register"),

    path('my-login', views.my_login, name="my-login"),

    

    # CRUD

    path('dashboard', views.dashboard, name="dashboard"),
    path('create-measure', views.create_measure, name="create-measure"),
    path('create-mission', views.create_mission, name="create-mission"),
    
    path('create-initiative', views.create_initiative, name="create-initiative"),
    
    
    path('create-quarterly-data', views.create_quarterly_data, name="create-quarterly-data"),
    path('view-quarterly-data', views.view_quarterly_data, name="view-quarterly-data"),
    
    
    # path('update-record/<int:pk>', views.update_record, name='update-record'),
    # path('record/<int:pk>', views.singular_record, name="record"),
    # path('delete-record/<int:pk>', views.delete_record, name="delete-record"),    
    
    
    # dependant dropdown list for Site and Location
    
    # path('load-locations', views.load_locations, name="load-locations"),   

    path('user-logout', views.user_logout, name="user-logout"),
    
    
]






