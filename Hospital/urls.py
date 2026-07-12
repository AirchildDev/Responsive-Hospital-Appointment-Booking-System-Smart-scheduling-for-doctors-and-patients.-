from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing page → Patient registration
    path('', views.patient_register, name='patient_register'),

    # Patient routes
    path('home/', views.patient_home, name='patient_home'),                 
    path('book/', views.book_appointment, name='book_appointment'),         
    path('appointment/<int:appointment_id>/update/', views.update_appointment, name='update_appointment'),  
    path('appointment/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),  

    # Doctor routes
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'), 
    path('doctor/appointment/<int:appointment_id>/update/', views.update_doctor_appointment, name='update_doctor_appointment'),  
    # path('doctor/appointment/<int:appointment_id>/delete/', views.delete_doctor_appointment, name='delete_doctor_appointment'),  

    # Authentication routes
    path('login/', views.custom_login, name='login'),   
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  

    # Password change (both form and success use the same template)
    path(
        'password_change/', 
        auth_views.PasswordChangeView.as_view(template_name='Hospital/password_change.html'), 
        name='password_change'
    ),
    path(
        'password_change/done/', 
        auth_views.PasswordChangeDoneView.as_view(template_name='Hospital/password_change.html'), 
        name='password_change_done'
    ),

    # Lists
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('patients/', views.patient_list, name='patient_list'),
    # path('logout/', views.custom_logout, name='logout'),

    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),

]
