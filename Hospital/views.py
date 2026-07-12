from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Doctor, Patient, Appointment
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import logout
from datetime import datetime
from django.utils import timezone


# Home/Landing page view
def home(request):
    if request.user.is_authenticated:
        try:
            Patient.objects.get(user=request.user)
            return redirect('patient_home')
        except Patient.DoesNotExist:
            try:
                Doctor.objects.get(user=request.user)
                return redirect('doctor_dashboard')
            except Doctor.DoesNotExist:
                pass
    # Render login page as home for unauthenticated users
    return render(request, 'Hospital/login.html')

# Patient signup view
def patient_register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # FIX: Prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('patient_register')

        user = User.objects.create_user(username=username, password=password)

        # FIX: Ensure age is stored as integer
        age = int(request.POST['age']) if request.POST.get('age') else None

        Patient.objects.create(
            user=user,
            age=age,
            phone=request.POST.get('phone', ''),   # FIX: safer access
            gender=request.POST.get('gender', 'Other')  # FIX: default fallback
        )
        messages.success(request, "Signup successful! Please login.")
        return redirect('login')
    return render(request, 'Hospital/patient_register.html')


# Custom login view to handle role-based routing
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'patient')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if role == 'doctor':
                # Check if user is a doctor
                try:
                    Doctor.objects.get(user=user)
                    return redirect('doctor_dashboard')
                except Doctor.DoesNotExist:
                    messages.error(request, "You are not registered as a doctor.")
                    return redirect('login')
            else:
                # Check if user is a patient
                try:
                    Patient.objects.get(user=user)
                    return redirect('patient_home')
                except Patient.DoesNotExist:
                    messages.error(request, "You are not registered as a patient.")
                    return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'Hospital/login.html')

# Patient home view: shows only their appointments
@login_required
def patient_home(request):
    try:
        patient = Patient.objects.get(user=request.user)
        appointments = Appointment.objects.filter(patient=patient)

        # Get current hour for greeting
        current_hour = timezone.localtime().hour

        return render(request, 'Hospital/patient_home.html', {
            'appointments': appointments,
            'current_hour': current_hour,
        })
    except Patient.DoesNotExist:
        messages.error(request, "You are not registered as a patient.")
        return redirect('login')
# Book appointment view
@login_required
def book_appointment(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "You are not registered as a patient.")
        return redirect('login')
    
    if request.method == "POST":
        doctor_id = request.POST.get('doctor')
        if not doctor_id:
            messages.error(request, "Doctor selection is required.")
            return redirect('book_appointment')

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # FIX: Validate date/time fields
        date = request.POST.get('date')
        time = request.POST.get('time')
        if not date or not time:
            messages.error(request, "Date and time are required.")
            return redirect('book_appointment')

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            description=request.POST.get('description', '')
        )
        messages.success(request, "Appointment booked successfully!")
        return redirect('patient_home')

    doctors = Doctor.objects.all()
    return render(request, 'Hospital/book_appointment.html', {'doctors': doctors})

# Update appointment for doctors
@login_required
def update_doctor_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if the logged-in user is the doctor assigned to this appointment
    try:
        doctor = Doctor.objects.get(user=request.user)
        if appointment.doctor != doctor:
            messages.error(request, "You can only update your own appointments.")
            return redirect('doctor_dashboard')
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('login')

    if request.method == "POST":
        appointment.date = request.POST.get('date', appointment.date)
        appointment.time = request.POST.get('time', appointment.time)
        appointment.description = request.POST.get('description', appointment.description)
        appointment.save()

        messages.success(request, "Appointment updated successfully!")
        return redirect('doctor_dashboard')

    # Pass all required flags to template
    return render(request, 'Hospital/book_appointment.html', {
        'appointment': appointment,
        'is_update': True,
        'is_doctor_update': True
    })

# Update appointment view (for patients to modify their appointments)
@login_required
def update_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    try:
        patient = Patient.objects.get(user=request.user)
        if appointment.patient != patient:
            messages.error(request, "You can only edit your own appointments.")
            return redirect('patient_home')
    except Patient.DoesNotExist:
        messages.error(request, "You are not registered as a patient.")
        return redirect('login')
    
    if request.method == "POST":
        doctor_id = request.POST.get('doctor', appointment.doctor.id)
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        appointment.doctor = doctor
        appointment.date = request.POST.get('date', appointment.date)
        appointment.time = request.POST.get('time', appointment.time)
        appointment.description = request.POST.get('description', appointment.description)
        appointment.save()
        
        messages.success(request, "Appointment updated successfully!")
        return redirect('patient_home')
    
    doctors = Doctor.objects.all()
    return render(request, 'Hospital/book_appointment.html', {
        'appointment': appointment,
        'doctors': doctors,
        'is_update': True
    })

# Delete appointment view (for patients to cancel their appointments)
@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the logged-in user is the patient who booked this appointment
    try:
        patient = Patient.objects.get(user=request.user)
        if appointment.patient != patient:
            messages.error(request, "You can only delete your own appointments.")
            return redirect('patient_home')
    except Patient.DoesNotExist:
        messages.error(request, "You are not registered as a patient.")
        return redirect('login')
    
    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted successfully!")
        return redirect('patient_home')
    
    # Reuse patient_home template for confirmation
    return render(request, 'Hospital/patient_home.html', {
        'appointment': appointment,
        'confirm_delete': True,
        'appointments': [appointment]
    })

# Doctor dashboard view: shows only appointments for the logged-in doctor
@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor)
        return render(request, 'Hospital/doctor_dashboard.html', {'appointments': appointments})
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('login')

# Update appointment for doctors
@login_required
def update_doctor_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the logged-in user is the doctor assigned to this appointment
    try:
        doctor = Doctor.objects.get(user=request.user)
        if appointment.doctor != doctor:
            messages.error(request, "You can only update your own appointments.")
            return redirect('doctor_dashboard')
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('login')
    
    if request.method == "POST":
        appointment.date = request.POST.get('date')
        appointment.time = request.POST.get('time')
        appointment.description = request.POST.get('description')
        appointment.save()
        
        messages.success(request, "Appointment updated successfully!")
        return redirect('doctor_dashboard')
    
    # Reuse doctor_dashboard for display
    return render(request, 'Hospital/book_appointment.html', {
        'appointment': appointment,
        'is_doctor_update': True
    })

# Delete appointment for doctors
# @login_required
# def delete_doctor_appointment(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id)
    
#     # Check if the logged-in user is the doctor assigned to this appointment
#     try:
#         doctor = Doctor.objects.get(user=request.user)
#         if appointment.doctor != doctor:
#             messages.error(request, "You can only delete your own appointments.")
#             return redirect('doctor_dashboard')
#     except Doctor.DoesNotExist:
#         messages.error(request, "You are not registered as a doctor.")
#         return redirect('login')
    
#     if request.method == "POST":
#         appointment.delete()
#         messages.success(request, "Appointment deleted successfully!")
#         return redirect('doctor_dashboard')
    
#     # Reuse doctor_dashboard for confirmation
#     return render(request, 'Hospital/doctor_dashboard.html', {
#         'appointment': appointment,
#         'confirm_delete': True,
#         'appointments': [appointment]
#     })

# views.py
@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'Hospital/doctor_list.html', {'doctors': doctors})

@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'Hospital/patient_list.html', {'patients': patients})

# def custom_logout(request):
#     logout(request)
#     return redirect('login')

# Hospital/views.py

from django.shortcuts import render

def about(request):
    return render(request, 'Hospital/about.html')

def gallery(request):
    return render(request, 'Hospital/gallery.html')

def contact(request):
    return render(request, 'Hospital/contact.html')



