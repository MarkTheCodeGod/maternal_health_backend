from rest_framework import generics
from django.shortcuts import render
from .models import Patient
from .serializers import PatientSerializer
from patient_activity.models import PatientActivityLog

# Dashboard view
def dashboard(request):
    return render(request, 'dashboard.html')

# Handles GET (list) and POST (create)
class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def perform_create(self, serializer):
        serializer.save()
        PatientActivityLog.objects.create(action='created')

# Handles GET (single), PUT (update), DELETE (remove)
class PatientRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def perform_update(self, serializer):
        serializer.save()
        PatientActivityLog.objects.create(action='updated')

    def perform_destroy(self, instance):
        instance.delete()
        PatientActivityLog.objects.create(action='deleted')
