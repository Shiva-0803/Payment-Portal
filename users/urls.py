from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('internal-login/', views.internal_login_view, name='internal_login'),
    path('login/', views.login_view, name='login'),
    path('otp/', views.otp_verify_view, name='otp_verify'),
    path('verify-password/', views.verify_password_view, name='verify_password'),
    path('register/', views.register_student_view, name='register_student'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('exam-dashboard/', views.exam_dashboard_view, name='exam_dashboard'),
    path('student/edit/<int:student_id>/', views.edit_student_view, name='edit_student'),
    path('student/delete/<int:student_id>/', views.delete_student_view, name='delete_student'),
    path('logout/', views.logout_view, name='logout'),
]
