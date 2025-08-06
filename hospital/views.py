from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import BaseUserForm, PatientForm

# Create your views here.
def home(requset) :
    return render(requset, 'hospital/index.html')

def aboutus(request) :
    return render(request, 'hospital/aboutus.html')

def contactus(request) :
    return render(request, 'hospital/contactus.html')

def patientlogin(request) :
    return render(request, 'hospital/patientlogin.html')

def patientsignup(request) :
    return render(request, 'hospital/patientsignup.html')


# def patientsignup(request):
#     if request.method == 'POST':
#         user_form = BaseUserForm(request.POST)
#         patient_form = PatientForm(request.POST)
        
#         if user_form.is_valid() and patient_form.is_valid():
#             user = user_form.save()
            
#             patient = patient_form.save(commit=False)
#             patient.user = user
#             patient.save()
            
#             login(request, user)
#             return redirect('patient-dashboard')  # Change this to your actual redirect
            
#     else:
#         user_form = BaseUserForm()
#         patient_form = PatientForm()
    
#     return render(request, 'hospital/patientsignup.html', {
#         'userForm': user_form,
#         'patientForm': patient_form
#     })

def adminlogin(request) :
    return render(request, 'hospital/adminlogin.html')

def adminsignup(request):
    return render(request, 'hospital/adminsignup.html')

def doctorlogin(request):
    return render(request, 'hospital/doctorlogin.html')

def doctorsignup(request):
    return render(request, 'hospital/doctorsignup.html')