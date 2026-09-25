from django.db import models

class PatientLog(models.Model):
    patient_id = models.IntegerField()
    action = models.CharField(max_length=50)  # created, updated, deleted
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - Patient {self.patient_id}"
