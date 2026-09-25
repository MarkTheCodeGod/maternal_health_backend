from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics
from .models import Patient
from .serializers import PatientSerializer
from patient_activity.models import PatientActivityLog

# Dashboard
@login_required
def dashboard(request):
    user = request.user
    context = {
        'is_admin': user.groups.filter(name='Admin').exists(),
        'is_editor': user.groups.filter(name='Editor').exists(),
        'is_viewer': user.groups.filter(name='Viewer').exists(),
    }
    return render(request, 'patients/dashboard.html', context)

# Create (POST)
@permission_required('patients.add_patient', raise_exception=True)
def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        stage = request.POST.get('stage', '')
        notes = request.POST.get('notes', '')
        patient = Patient.objects.create(name=name, age=age, stage=stage, notes=notes)
        PatientActivityLog.objects.create(action='created', patient=patient)
        return redirect('view_patient')
    return render(request, 'patients/add_patient.html')

# Read (GET)
@permission_required('patients.view_patient', raise_exception=True)
def view_patient(request):
    patients = Patient.objects.all()
    user = request.user
    context = {
        'patients': patients,
        'is_admin': user.groups.filter(name='Admin').exists(),
        'is_editor': user.groups.filter(name='Editor').exists(),
        'is_viewer': user.groups.filter(name='Viewer').exists(),
    }
    return render(request, 'patients/view_patient.html', context)

# Update (PUT)
@permission_required('patients.change_patient', raise_exception=True)
def update_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.age = request.POST.get('age')
        patient.stage = request.POST.get('stage', '')
        patient.notes = request.POST.get('notes', '')
        patient.save()
        PatientActivityLog.objects.create(action='updated', patient=patient)
        return redirect('view_patient')
    return render(request, 'patients/update_patient.html', {'patient': patient})

# Delete (DELETE)
@permission_required('patients.delete_patient', raise_exception=True)
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        PatientActivityLog.objects.create(action='deleted', patient=patient)
        patient.delete()
        return redirect('view_patient')
    return render(request, 'patients/delete_patient.html', {'patient': patient})

# API endpoints (Postman)
class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def perform_create(self, serializer):
        patient = serializer.save()
        PatientActivityLog.objects.create(action='created', patient=patient)

class PatientRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def perform_update(self, serializer):
        patient = serializer.save()
        PatientActivityLog.objects.create(action='updated', patient=patient)

    def perform_destroy(self, instance):
        PatientActivityLog.objects.create(action='deleted', patient=instance)
        instance.delete()
