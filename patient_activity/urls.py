from django.urls import path
from .views import patient_logs

urlpatterns = [
    path('patient-logs/', patient_logs, name='patient-logs'),
]
