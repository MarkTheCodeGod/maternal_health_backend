from django.db import models
from django.contrib.auth.models import User

class PatientActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    # ForeignKey becomes NULL when a patient is deleted
    patient = models.ForeignKey(
        'patients.Patient', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # Stable identifier preserved forever even when patient is deleted!
    patient_identifier = models.CharField(max_length=255, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        label = self.patient_identifier or (self.patient.name if self.patient else "Deleted Patient")
        user_label = self.user.username if self.user else "System"
        return f"{user_label} ({self.role}) {self.action} - {label}"