
from django.urls import path
from django.conf.urls import (handler404)
from . import views
from .views import GeneratePdf

handler404 = 'webapp.views.handler404'

urlpatterns = [

    path('', views.home, name=""),

    path('register', views.register, name="register"),

    path('my-login', views.my_login, name="my-login"),

    path('profile',views.profile, name='profile'),
    path('next-fiscal-year',views.next_fiscal_year, name='next-fiscal-year'),

    

    # CRUD

    path('dashboard', views.dashboard, name="dashboard"),
    # path('dashboard2/', views.Dashboard2.as_view(), name="dashboard2"),
    
    path('create-measure/', views.create_measure, name="create-measure"),
    path('create-mission/', views.create_mission, name="create-mission"),
    path('create-overview/', views.create_overview, name="create-overview"),
    path('create-objective/', views.create_objective, name="create-objective"),
    
    path('create-initiative', views.create_initiative, name="create-initiative"),
    
    
    path('create-quarterly-data/<int:pk>/<str:quarter>', views.create_quarterly_data, name="create-quarterly-data"),
    path('view-quarterly-data/<int:pk>', views.view_quarterly_data, name="view-quarterly-data"),
    


    path('user-logout', views.user_logout, name="user-logout"),
    

    path('pdf/', GeneratePdf.as_view(), name="pdf"),

    
    
]






