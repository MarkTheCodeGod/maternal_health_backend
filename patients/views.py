from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, viewsets, parsers, permissions
from .models import Patient, Content
from .serializers import PatientSerializer, ContentSerializer
from patient_activity.models import PatientActivityLog

# --- Custom API Permission ---
class CanDeletePatient(permissions.BasePermission):
    """
    Ensures only users with 'patients.delete_patient' permission or staff can delete a patient.
    """
    def has_permission(self, request, view):
        if request.method == 'DELETE':
            return request.user and (request.user.is_staff or request.user.has_perm('patients.delete_patient'))
        return True


# --- HTML Dashboard & Views ---
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


# --- REST API Endpoints ---
class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        patient = serializer.save()
        PatientActivityLog.objects.create(action='created', patient=patient)

class PatientRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, CanDeletePatient]

    def perform_update(self, serializer):
        patient = serializer.save()
        PatientActivityLog.objects.create(action='updated', patient=patient)

    def perform_destroy(self, instance):
        PatientActivityLog.objects.create(action='deleted', patient=instance)
        instance.delete()


# Content API with filtering and authentication
class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Content.objects.all()
        language = self.request.query_params.get('language')
        topic = self.request.query_params.get('topic')
        stage = self.request.query_params.get('stage')

        # Filter if parameters are provided in query string
        if language:
            queryset = queryset.filter(language__iexact=language)
        if topic:
            queryset = queryset.filter(topic__iexact=topic)
        if stage:
            queryset = queryset.filter(stage__iexact=stage)

        return queryset