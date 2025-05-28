from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='home'),  # Redirect root URL to login page
    path('reports/', views.reports, name='reports'),
    path('login/', views.user_login, name='login'),
    path('create_account/', views.create_account, name='create_account'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance, name='attendance'),
    path('upload_attendance/', views.upload_attendance, name='upload_attendance'),
    path('download_attendance_template/', views.download_attendance_template, name='download_attendance_template'),
    path('clear_attendance/', views.clear_attendance, name='clear_attendance'),
    path('add_employees/', views.add_employees, name='add_employees'),
    path('payroll_computations/', views.payroll_computations, name='payroll_computations'),
    path('personnel_profile/', views.personnel_profile, name='personnel_profile'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('remove_employees/', views.remove_employees, name='remove_employees'),
    path('logout/', views.user_logout, name='logout'),
]