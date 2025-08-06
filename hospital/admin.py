from django.contrib import admin
from .models import Doctor, Patient, Appointment, PatientDischargeDetails, AdminApproval

# Register your models here.
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'department', 'mobile', 'status', 'is_approved', 'get_id')
    list_filter = ('department', 'status', 'is_approved')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'mobile')
    readonly_fields = ('get_id', 'approved_by', 'approved_date')
    actions = ['approve_doctors', 'reject_doctors']
    
    def get_name(self, obj):
        return obj.get_name
    get_name.short_description = 'Name'
    
    def get_id(self, obj):
        return obj.get_id
    get_id.short_description = 'User ID'
    
    def approve_doctors(self, request, queryset):
        queryset.update(is_approved=True)
    approve_doctors.short_description = "Approve selected doctors"
    
    def reject_doctors(self, request, queryset):
        queryset.delete()
    reject_doctors.short_description = "Reject and delete selected doctors"

admin.site.register(Doctor, DoctorAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'mobile', 'symptoms', 'assignedDoctorId', 'admitDate', 'status', 'get_id')
    list_filter = ('status', 'admitDate', 'assignedDoctorId')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'mobile', 'symptoms')
    readonly_fields = ('get_id', 'admitDate')
    
    def get_name(self, obj):
        return obj.get_name
    get_name.short_description = 'Name'
    
    def get_id(self, obj):
        return obj.get_id
    get_id.short_description = 'User ID'

admin.site.register(Patient, PatientAdmin)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patientName', 'doctorName', 'appointmentDate', 'status', 'is_accepted_by_doctor', 'get_id')
    list_filter = ('status', 'appointmentDate', 'is_accepted_by_doctor')
    search_fields = ('patientName', 'doctorName', 'description')
    readonly_fields = ('appointmentDate', 'accepted_date')
    actions = ['approve_appointments', 'mark_doctor_accepted']
    
    def get_id(self, obj):
        return obj.id
    get_id.short_description = 'Appointment ID'
    
    def approve_appointments(self, request, queryset):
        queryset.update(status=True)
    approve_appointments.short_description = "Approve selected appointments"
    
    def mark_doctor_accepted(self, request, queryset):
        queryset.update(is_accepted_by_doctor=True)
    mark_doctor_accepted.short_description = "Mark as accepted by doctor"

admin.site.register(Appointment, AppointmentAdmin)

class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    list_display = ('patientName', 'assignedDoctorName', 'admitDate', 'releaseDate', 'total', 'get_id')
    list_filter = ('admitDate', 'releaseDate')
    search_fields = ('patientName', 'assignedDoctorName', 'mobile')
    readonly_fields = ('get_id',)
    
    def get_id(self, obj):
        return obj.id
    get_id.short_description = 'Discharge ID'

admin.site.register(PatientDischargeDetails, PatientDischargeDetailsAdmin)

class AdminApprovalAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'approved_by', 'created_date', 'approved_date')
    list_filter = ('is_approved', 'created_date', 'approved_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_date', 'approved_date')
    actions = ['approve_admins', 'reject_admins']
    
    def approve_admins(self, request, queryset):
        queryset.update(is_approved=True)
    approve_admins.short_description = "Approve selected admins"
    
    def reject_admins(self, request, queryset):
        for approval in queryset:
            approval.user.delete()
        queryset.delete()
    reject_admins.short_description = "Reject and delete selected admins"

admin.site.register(AdminApproval, AdminApprovalAdmin)