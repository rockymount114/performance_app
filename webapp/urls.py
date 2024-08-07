
from django.urls import path
from django.conf.urls import (handler404)
from . import views
from .views import GeneratePdf, GeneratePdf2, GeneratePdf3
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


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
    path('view-objective-info/<int:pk>/', views.view_objective_info, name="view-objective-info"),
    path('view-measure-info/<int:pk>/', views.view_measure_info, name="view-measure-info"),
    path('view-focus-area-info/<int:pk>/', views.view_focus_area_info, name="view-focus-area-info"),
    path('update-session/', views.update_session, name='update-session'),
    
    # View and update records --> regular  
    path('update-objective/<int:pk>/', views.update_objective, name="update-objective"),
    path('view-objective-info-regular/<int:pk>/', views.view_objective_info_regular, name="view-objective-info-regular"),
 
    path('update-measure/<int:pk>/', views.update_measure, name="update-measure"),
    path('view-measure-info-regular/<int:pk>/', views.view_measure_info_regular, name="view-measure-info-regular"),

    path('update-initiative/<int:pk>/', views.update_initiative, name="update-initiative"),


    # Grant extension:
    path('request-extension/', views.request_extension, name='request-extension'),
    path('grant-extension/', views.grant_extension, name='grant-extension'),
    path('extension-log/', views.extension_log, name='extension-log'),




    path('user-logout/', views.user_logout, name="user-logout"),
    
    # pdf
    path('pdf/', GeneratePdf.as_view(), name="pdf"),
    path('pdf2/', GeneratePdf2.as_view(), name="pdf2"),
     path('pdf3/', GeneratePdf3.as_view(), name="pdf3"),
    # path('pdf2/', views.render_pdf, name="pdf2"),
    # path('pdf_download/', views.render_pdf_view, name='pdf_download'),
    
    # Password reset
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='webapp/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='webapp/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='webapp/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='webapp/password_reset_complete.html'), name='password_reset_complete'),   

    # admin_forms:
    path('admin-forms/', views.admin_forms, name='admin-forms'),
    
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'), 
    
] 

# if settings.DEBUG:
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    




