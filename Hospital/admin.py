from django.contrib import admin
from .models import Doctor, Patient, Appointment

# Admin panel customization for Doctor
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialization', 'phone', 'gender')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'

# Admin panel customization for Patient
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'age', 'phone', 'gender')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'

# Admin panel customization for Appointment
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'date', 'time')

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    get_patient_name.short_description = 'Patient'

    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    get_doctor_name.short_description = 'Doctor'
