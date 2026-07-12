from django.db import models
from django.contrib.auth.models import User

# Doctor model: linked to Django's built-in User model
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each doctor has a user account
    specialization = models.CharField(max_length=100)            # Doctor's field of expertise
    phone = models.CharField(max_length=15, blank=True)          # Optional phone number
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        default='Male'
    )

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"

from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each patient has a user account
    age = models.PositiveIntegerField(blank=True, null=True)     # Patient's age (optional, allows nulls)
    phone = models.CharField(max_length=15, blank=True)          # Optional phone number
    gender = models.CharField(                                   # Gender field
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        default='Male'
    )

    def __str__(self):
        # Show full name if available, otherwise username
        return self.user.get_full_name() or self.user.username

# Appointment model: connects Patient and Doctor
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)  # Appointment belongs to a patient
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)    # Appointment is with a doctor
    date = models.DateField()                                       # Appointment date
    time = models.TimeField()                                       # Appointment time
    description = models.TextField(blank=True)                      # Optional notes

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.time}"
