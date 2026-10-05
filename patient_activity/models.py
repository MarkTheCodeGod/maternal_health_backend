from django.db import models
from django.contrib.auth.models import User

class PatientActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    # Change to SET_NULL so deleting a patient DOES NOT delete the audit log history
    patient = models.ForeignKey(
        'patients.Patient', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        patient_label = self.patient.name if self.patient else "Deleted Patient"
        return f"{self.user} ({self.role}) {self.action} {patient_label}"