from django.db import models
from patients.models import Patient, Content

class ActivityLog(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="activity_logs")
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=50)  # e.g. "viewed", "completed"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} {self.action} {self.content.title} at {self.timestamp}"
