"""
URL configuration for hospital_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('contactus/', views.contactus, name='contactus'),
    
    # Patient URLs
    path('patientsignup/', views.patientsignup, name='patientsignup'),
    path('patient-dashboard/', views.patient_dashboard, name='patient-dashboard'),
    path('book-appointment/', views.book_appointment, name='book-appointment'),
    
    # Admin URLs
    path('adminsignup/', views.adminsignup, name='adminsignup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin-doctors/', views.admin_doctors, name='admin-doctors'),
    path('admin-patients/', views.admin_patients, name='admin-patients'),
    path('admin-appointments/', views.admin_appointments, name='admin-appointments'),
    path('admin-pending-approvals/', views.admin_pending_approvals, name='admin-pending-approvals'),
    
    # Admin approval actions
    path('approve-appointment/<int:appointment_id>/', views.approve_appointment, name='approve-appointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='delete-appointment'),
    path('approve-doctor/<int:doctor_id>/', views.approve_doctor, name='approve-doctor'),
    path('reject-doctor/<int:doctor_id>/', views.reject_doctor, name='reject-doctor'),
    path('approve-admin/<int:admin_id>/', views.approve_admin, name='approve-admin'),
    path('reject-admin/<int:admin_id>/', views.reject_admin, name='reject-admin'),
    
    # Doctor URLs
    path('doctorsignup/', views.doctorsignup, name='doctorsignup'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor-dashboard'),
    path('accept-appointment/<int:appointment_id>/', views.accept_appointment, name='accept-appointment'),
    
    # Role-based redirection
    path('adminclick/', views.admin_click, name='admin-click'),
    path('doctorclick/', views.doctor_click, name='doctor-click'),
    path('patientclick/', views.patient_click, name='patient-click'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
    path('patientlogin/', views.patientlogin, name='patientlogin'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('doctorlogin/', views.doctorlogin, name='doctorlogin'),
]

# Add static files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
