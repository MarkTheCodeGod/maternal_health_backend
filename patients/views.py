from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, viewsets, parsers, permissions
from .models import Patient, Content
from .serializers import PatientSerializer, ContentSerializer
from patient_activity.models import PatientActivityLog


# --- Helper to determine user role ---
def get_user_role(user):
    if not user or not user.is_authenticated:
        return 'Anonymous'
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return 'Admin'
    if user.groups.filter(name='Editor').exists():
        return 'Editor'
    if user.groups.filter(name='Viewer').exists():
        return 'Viewer'
    return 'Staff' if user.is_staff else 'Unassigned'


# --- Custom API Permissions ---
class PatientPermission(permissions.BasePermission):
    """
    Role-Based API Permissions:
    - GET / HEAD / OPTIONS: Allowed for any authenticated user (Admin, Editor, Viewer).
    - POST / PUT / PATCH: Allowed only for Admin and Editor. Viewers get 403 Forbidden.
    - DELETE: Allowed only for Admin, staff, or users with delete_patient permission.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Safe read-only methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin / Superuser has full access
        if request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name='Admin').exists():
            return True

        # Create & Update: Editor only (or explicit model perms)
        if request.method in ['POST', 'PUT', 'PATCH']:
            is_editor = request.user.groups.filter(name='Editor').exists()
            has_perm = request.user.has_perm('patients.add_patient') or request.user.has_perm('patients.change_patient')
            return is_editor or has_perm

        # Delete: Admin or explicit delete permission only
        if request.method == 'DELETE':
            return request.user.has_perm('patients.delete_patient')

        return False


class ContentPermission(permissions.BasePermission):
    """
    Content API Permissions:
    - GET: All authenticated users (Admin, Editor, Viewer).
    - POST / PUT / PATCH: Admin and Editor only.
    - DELETE: Admin only.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name='Admin').exists():
            return True

        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.groups.filter(name='Editor').exists() or request.user.has_perm('patients.add_content')

        if request.method == 'DELETE':
            return request.user.has_perm('patients.delete_content')

        return False


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
        PatientActivityLog.objects.create(
            action='created',
            patient=patient,
            patient_identifier=f"Patient #{patient.id} ({patient.name})",
            user=request.user,
            role=get_user_role(request.user)
        )
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
        PatientActivityLog.objects.create(
            action='updated',
            patient=patient,
            patient_identifier=f"Patient #{patient.id} ({patient.name})",
            user=request.user,
            role=get_user_role(request.user)
        )
        return redirect('view_patient')
    return render(request, 'patients/update_patient.html', {'patient': patient})

# Delete (DELETE)
@permission_required('patients.delete_patient', raise_exception=True)
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient_label = f"Patient #{patient.id} ({patient.name})"
        PatientActivityLog.objects.create(
            action='deleted',
            patient=patient,
            patient_identifier=patient_label,
            user=request.user,
            role=get_user_role(request.user)
        )
        patient.delete()
        return redirect('view_patient')
    return render(request, 'patients/delete_patient.html', {'patient': patient})


# --- REST API Endpoints ---
class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, PatientPermission]

    def perform_create(self, serializer):
        patient = serializer.save()
        PatientActivityLog.objects.create(
            action='created',
            patient=patient,
            patient_identifier=f"Patient #{patient.id} ({patient.name})",
            user=self.request.user,
            role=get_user_role(self.request.user)
        )

class PatientRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, PatientPermission]

    def perform_update(self, serializer):
        patient = serializer.save()
        PatientActivityLog.objects.create(
            action='updated',
            patient=patient,
            patient_identifier=f"Patient #{patient.id} ({patient.name})",
            user=self.request.user,
            role=get_user_role(self.request.user)
        )

    def perform_destroy(self, instance):
        patient_label = f"Patient #{instance.id} ({instance.name})"
        PatientActivityLog.objects.create(
            action='deleted',
            patient=instance,
            patient_identifier=patient_label,
            user=self.request.user,
            role=get_user_role(self.request.user)
        )
        instance.delete()


# Content API with filtering and authentication
class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    permission_classes = [permissions.IsAuthenticated, ContentPermission]

    def get_queryset(self):
        queryset = Content.objects.all()
        language = self.request.query_params.get('language')
        topic = self.request.query_params.get('topic')
        stage = self.request.query_params.get('stage')

        if language:
            queryset = queryset.filter(language__iexact=language)
        if topic:
            queryset = queryset.filter(topic__iexact=topic)
        if stage:
            queryset = queryset.filter(stage__iexact=stage)

        return queryset