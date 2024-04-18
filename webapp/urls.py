
from django.urls import path
from django.conf.urls import (handler404)
from . import views
from .views import GeneratePdf
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'webapp.views.handler404'

urlpatterns = [

    path('', views.home, name=""),
    path('register', views.register, name="register"),
    path('my-login', views.my_login, name="my-login"),
    path('approvals',views.approvals, name='approvals'),
    path('profile/',views.profile, name='profile'),

    # CRUD
    path('dashboard/', views.dashboard, name="dashboard"),
    
    path('create-measure/', views.create_measure, name="create-measure"),
    path('create-mission/', views.create_mission, name="create-mission"),
    path('create-overview/', views.create_overview, name="create-overview"),
    path('create-objective/', views.create_objective, name="create-objective"),
    path('create-focus-area/', views.create_focus_area, name="create-focus-area"),    
    path('create-initiative/', views.create_initiative, name="create-initiative"),
    

    path('create-quarterly-data/<int:pk>/<str:quarter>/', views.create_quarterly_data, name="create-quarterly-data"),
    path('create-initiative-detail/<int:pk>/', views.create_initiative_detail, name="create-initiative-detail"),
    path('view-quarterly-data/<int:pk>/', views.view_quarterly_data, name="view-quarterly-data"),
    path('view-initiative-detail/<int:pk>/', views.view_initiative_detail, name="view-initiative-detail"),
    


    path('user-logout/', views.user_logout, name="user-logout"),
    
    # pdf
    path('pdf/', GeneratePdf.as_view(), name="pdf"),
    # path('pdf2/', views.render_pdf, name="pdf2"),
    # path('pdf_download/', views.render_pdf_view, name='pdf_download'),
    
    # Profile images    
    
] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)






