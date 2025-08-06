from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from . import models
from datetime import datetime

class BaseUserForm(forms.ModelForm):
    """Base form for user creation with common fields"""
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter a strong password',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
    }), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# Admin signup
class AdminSigupForm(BaseUserForm):
    class Meta(BaseUserForm.Meta):
        help_texts = {
            'username': 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        }

# Doctor forms
class DoctorUserForm(BaseUserForm):
    pass

class DoctorForm(forms.ModelForm):
    class Meta:
        model = models.Doctor
        fields = ['address', 'mobile', 'department', 'status', 'profile_pic']
        widgets = {
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'mobile': forms.TextInput(attrs={
                'placeholder': 'Enter 10 digit mobile number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if len(str(mobile)) != 10:
            raise ValidationError("Mobile number must be 10 digits")
        return mobile

# Patient forms
class PatientUserForm(BaseUserForm):
    pass

class PatientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Safely filter doctors based on available fields
        try:
            # Try to filter by is_approved if the field exists
            doctors = models.Doctor.objects.filter(status=True, is_approved=True)
        except:
            # Fallback to just status if is_approved doesn't exist
            doctors = models.Doctor.objects.filter(status=True)
        
        self.fields['assignedDoctor'] = forms.ModelChoiceField(
            queryset=doctors,
            empty_label="Select Doctor",
            label="Assigned Doctor",
            help_text="Select your primary doctor",
            required=False
        )

    class Meta:
        model = models.Patient
        fields = ['address', 'mobile', 'status', 'symptoms', 'assignedDoctor', 'profile_pic']
        widgets = {
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'symptoms': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe your symptoms',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'mobile': forms.TextInput(attrs={
                'placeholder': 'Enter 10 digit mobile number',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }),
            'profile_pic': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

# Appointment forms
class AppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Safely filter doctors based on available fields
        try:
            doctors = models.Doctor.objects.filter(status=True, is_approved=True)
        except:
            doctors = models.Doctor.objects.filter(status=True)
        
        try:
            patients = models.Patient.objects.filter(status=True)
        except:
            patients = models.Patient.objects.all()
        
        self.fields['doctorId'] = forms.ModelChoiceField(
            queryset=doctors,
            empty_label="Select Doctor",
            to_field_name="user_id",
            label="Doctor"
        )
        self.fields['patientId'] = forms.ModelChoiceField(
            queryset=patients,
            empty_label="Select Patient",
            to_field_name="user_id",
            label="Patient"
        )
    
    admin_scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=False,
        label="Admin Scheduled Date"
    )
    admin_scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=False,
        label="Admin Scheduled Time"
    )

    class Meta:
        model = models.Appointment
        fields = ['description', 'status', 'admin_scheduled_date', 'admin_scheduled_time']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PatientAppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Safely filter doctors based on available fields
        try:
            doctors = models.Doctor.objects.filter(status=True, is_approved=True)
        except:
            doctors = models.Doctor.objects.filter(status=True)
        
        self.fields['doctorId'] = forms.ModelChoiceField(
            queryset=doctors,
            empty_label="Select Doctor",
            to_field_name="user_id",
            label="Doctor"
        )

    class Meta:
        model = models.Appointment
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your symptoms and reason for appointment'}),
        }

class DoctorScheduleForm(forms.ModelForm):
    doctor_scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=True,
        label="Appointment Date"
    )
    doctor_scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=True,
        label="Appointment Time"
    )

    class Meta:
        model = models.Appointment
        fields = ['doctor_scheduled_date', 'doctor_scheduled_time']

# Contact us form
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'placeholder': 'Your name'
    }))
    Email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address'
    }))
    Phone = forms.IntegerField(widget=forms.NumberInput(attrs={
        'placeholder': 'Your phone number'
    }))
    Message = forms.CharField(max_length=500, widget=forms.Textarea(attrs={
        'rows': 3,
        'placeholder': 'Your message here...'
    }))

# Admin approval form
class AdminApprovalForm(forms.ModelForm):
    class Meta:
        model = models.AdminApproval
        fields = ['is_approved']
        widgets = {
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }