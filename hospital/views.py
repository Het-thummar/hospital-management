from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, date
from .forms import (
    BaseUserForm, PatientForm, DoctorUserForm, DoctorForm, 
    AdminSigupForm, AppointmentForm, PatientAppointmentForm, 
    DoctorScheduleForm, ContactusForm, AdminApprovalForm
)
from .models import Doctor, Patient, Appointment, PatientDischargeDetails, AdminApproval
from django.utils import timezone

# Create your views here.
def home(request):
    return render(request, 'hospital/index.html')

def aboutus(request):
    return render(request, 'hospital/aboutus.html')

def contactus(request):
    if request.method == 'POST':
        form = ContactusForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contactus')
    else:
        form = ContactusForm()
    
    return render(request, 'hospital/contactus.html', {'form': form})

# Authentication Views
def patientlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                patient = Patient.objects.get(user=user)
                login(request, user)
                request.session['alert_message'] = 'Login successful!'
                return redirect('patient-dashboard')
            except Patient.DoesNotExist:
                request.session['alert_message'] = 'You are not registered as a patient.'
        else:
            request.session['alert_message'] = 'Invalid username or password.'
    return render(request, 'hospital/patientlogin.html')

def patientsignup(request):
    if request.method == 'POST':
        user_form = BaseUserForm(request.POST)
        patient_form = PatientForm(request.POST, request.FILES)
        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save()
            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()
            login(request, user)
            request.session['alert_message'] = 'Signup successful!'
            return redirect('patient-dashboard')
        else:
            request.session['alert_message'] = 'Please correct the errors below.'
    else:
        user_form = BaseUserForm()
        patient_form = PatientForm()
    return render(request, 'hospital/patientsignup.html', {
        'userForm': user_form,
        'patientForm': patient_form
    })

def adminlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['alert_message'] = 'Login successful!'
            return redirect('admin-dashboard')
        else:
            request.session['alert_message'] = 'Invalid username or password.'
    return render(request, 'hospital/adminlogin.html')

def adminsignup(request):
    if request.method == 'POST':
        form = AdminSigupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create admin approval entry
            AdminApproval.objects.create(user=user, is_approved=False)
            login(request, user)
            request.session['alert_message'] = 'Signup successful!'
            return redirect('admin-dashboard')
        else:
            request.session['alert_message'] = 'Please correct the errors below.'
    else:
        form = AdminSigupForm()
    return render(request, 'hospital/adminsignup.html', {'form': form})

def doctorlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                doctor = Doctor.objects.get(user=user)
                login(request, user)
                request.session['alert_message'] = 'Login successful!'
                return redirect('doctor-dashboard')
            except Doctor.DoesNotExist:
                request.session['alert_message'] = 'You are not registered as a doctor.'
        else:
            request.session['alert_message'] = 'Invalid username or password.'
    return render(request, 'hospital/doctorlogin.html')

def doctorsignup(request):
    if request.method == 'POST':
        user_form = DoctorUserForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)
        if user_form.is_valid() and doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            login(request, user)
            request.session['alert_message'] = 'Signup successful!'
            return redirect('doctor-dashboard')
        else:
            request.session['alert_message'] = 'Please correct the errors below.'
    else:
        user_form = DoctorUserForm()
        doctor_form = DoctorForm()
    return render(request, 'hospital/doctorsignup.html', {
        'userForm': user_form,
        'doctorForm': doctor_form
    })

# Patient Views
@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
        appointments = Appointment.objects.filter(patientId=patient.user.id).order_by('-createdDate')
        
        context = {
            'patient': patient,
            'appointments': appointments,
        }
        context['alert_message'] = request.session.pop('alert_message', None)
        return render(request, 'hospital/patient_dashboard.html', context)
    except Patient.DoesNotExist:
        request.session['alert_message'] = 'Patient profile not found. Please contact support.'
        return redirect('patientlogin')

@login_required
def book_appointment(request):
    try:
        patient = Patient.objects.get(user=request.user)
        
        if request.method == 'POST':
            form = PatientAppointmentForm(request.POST)
            
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.patientId = patient.user.id
                appointment.patientName = patient.get_name
                appointment.doctorId = form.cleaned_data['doctorId'].user.id
                appointment.doctorName = form.cleaned_data['doctorId'].get_name
                appointment.save()
                
                messages.success(request, 'Appointment booked successfully! Waiting for doctor approval.')
                return redirect('patient-dashboard')
        else:
            form = PatientAppointmentForm()
        
        return render(request, 'hospital/book_appointment.html', {'form': form})
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')

# Admin Views
@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    pending_doctor_approvals = Doctor.objects.filter(is_approved=False).count()
    pending_admin_approvals = AdminApproval.objects.filter(is_approved=False).count()
    
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'pending_doctor_approvals': pending_doctor_approvals,
        'pending_admin_approvals': pending_admin_approvals,
    }
    context['alert_message'] = request.session.pop('alert_message', None)
    return render(request, 'hospital/admin_dashboard.html', context)

@login_required
def admin_doctors(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    doctors = Doctor.objects.all().order_by('-id')
    return render(request, 'hospital/admin_doctors.html', {'doctors': doctors})

@login_required
def admin_patients(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    patients = Patient.objects.all().order_by('-id')
    return render(request, 'hospital/admin_patients.html', {'patients': patients})

@login_required
def admin_appointments(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    appointments = Appointment.objects.all().order_by('-createdDate')
    return render(request, 'hospital/admin_appointments.html', {'appointments': appointments})

@login_required
def admin_pending_approvals(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    pending_doctors = Doctor.objects.filter(is_approved=False)
    pending_admins = AdminApproval.objects.filter(is_approved=False)
    
    context = {
        'pending_doctors': pending_doctors,
        'pending_admins': pending_admins,
    }
    context['alert_message'] = request.session.pop('alert_message', None)
    return render(request, 'hospital/admin_pending_approvals.html', context)

# Admin Action Views
@login_required
def approve_appointment(request, appointment_id):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = True
    appointment.save()
    
    messages.success(request, f'Appointment for {appointment.patientName} approved successfully.')
    return redirect('admin-appointments')

@login_required
def delete_appointment(request, appointment_id):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    patient_name = appointment.patientName
    appointment.delete()
    
    messages.success(request, f'Appointment for {patient_name} deleted successfully.')
    return redirect('admin-appointments')

@login_required
def approve_doctor(request, doctor_id):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_approved = True
    doctor.approved_by = request.user
    doctor.approved_date = datetime.now()
    doctor.save()
    
    messages.success(request, f'Doctor {doctor.get_name} approved successfully.')
    return redirect('admin-pending-approvals')

@login_required
def reject_doctor(request, doctor_id):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin privileges required.'
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor_name = doctor.get_name
    doctor.user.delete()  # This will cascade delete the doctor record
    
    messages.success(request, f'Doctor {doctor_name} rejected and removed successfully.')
    return redirect('admin-pending-approvals')

@login_required
def approve_admin(request, admin_id):
    if not request.user.is_superuser:
        request.session['alert_message'] = 'Access denied. Super admin privileges required.'
        return redirect('home')
    
    admin_approval = get_object_or_404(AdminApproval, id=admin_id)
    admin_approval.is_approved = True
    admin_approval.approved_by = request.user
    admin_approval.approved_date = datetime.now()
    admin_approval.save()
    
    # Add user to Admin group
    admin_group, created = Group.objects.get_or_create(name='Admin')
    admin_approval.user.groups.add(admin_group)
    
    messages.success(request, f'Admin {admin_approval.user.get_full_name()} approved successfully.')
    return redirect('admin-pending-approvals')

@login_required
def reject_admin(request, admin_id):
    if not request.user.is_superuser:
        request.session['alert_message'] = 'Access denied. Super admin privileges required.'
        return redirect('home')
    
    admin_approval = get_object_or_404(AdminApproval, id=admin_id)
    admin_name = admin_approval.user.get_full_name()
    admin_approval.user.delete()  # This will cascade delete the approval record
    
    messages.success(request, f'Admin {admin_name} rejected and removed successfully.')
    return redirect('admin-pending-approvals')

@login_required
def approve_patient(request, patient_id):
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists() or 
            AdminApproval.objects.filter(user=request.user, is_approved=True).exists() or
            Doctor.objects.filter(user=request.user, is_approved=True).exists()):
        request.session['alert_message'] = 'Access denied. Admin or Doctor privileges required.'
        return redirect('home')
    
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        # Set approval fields
        patient.is_approved = True
        patient.approved_by = request.user
        patient.approved_at = timezone.now()
        patient.save()
        
        # Create appointment if date and time are provided
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        if appointment_date and appointment_time:
            Appointment.objects.create(
                patientId=patient.user.id,
                doctorId=request.user.id if hasattr(request.user, 'doctor') else None,
                patientName=patient.get_name,
                doctorName=request.user.get_full_name(),
                appointmentDate=appointment_date,
                appointmentTime=appointment_time,
                status=True
            )
            request.session['alert_message'] = f'Patient {patient.get_name} approved and appointment scheduled for {appointment_date} at {appointment_time}.'
        else:
            request.session['alert_message'] = f'Patient {patient.get_name} approved successfully.'
        
        return redirect('admin-dashboard')
    
    return render(request, 'hospital/approve_patient.html', {'patient': patient})

# Doctor Views
@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        
        # Get appointments for this doctor
        appointments = Appointment.objects.filter(doctorId=doctor.user.id).order_by('-createdDate')
        pending_appointments = appointments.filter(is_accepted_by_doctor=False)
        accepted_appointments = appointments.filter(is_accepted_by_doctor=True)
        
        context = {
            'doctor': doctor,
            'appointments': appointments,
            'pending_appointments': pending_appointments,
            'accepted_appointments': accepted_appointments,
        }
        context['alert_message'] = request.session.pop('alert_message', None)
        return render(request, 'hospital/doctor_dashboard.html', context)
    except Doctor.DoesNotExist:
        request.session['alert_message'] = 'Doctor profile not found. Please contact support.'
        return redirect('doctorlogin')

@login_required
def accept_appointment(request, appointment_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = get_object_or_404(Appointment, id=appointment_id, doctorId=doctor.user.id)
        
        if request.method == 'POST':
            form = DoctorScheduleForm(request.POST)
            if form.is_valid():
                appointment.is_accepted_by_doctor = True
                appointment.accepted_date = datetime.now()
                appointment.doctor_scheduled_date = form.cleaned_data['doctor_scheduled_date']
                appointment.doctor_scheduled_time = form.cleaned_data['doctor_scheduled_time']
                appointment.save()
                
                messages.success(request, 'Appointment accepted and scheduled successfully.')
                return redirect('doctor-dashboard')
        else:
            form = DoctorScheduleForm()
        
        return render(request, 'hospital/schedule_appointment.html', {
            'form': form,
            'appointment': appointment
        })
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')

# Role-based redirection views
def admin_click(request):
    if request.user.is_authenticated:
        return redirect('admin-dashboard')
    return redirect('adminlogin')

def doctor_click(request):
    if request.user.is_authenticated:
        return redirect('doctor-dashboard')
    return redirect('doctorlogin')

def patient_click(request):
    if request.user.is_authenticated:
        return redirect('patient-dashboard')
    return redirect('patientlogin')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')