from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    stage = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Content(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="contents")
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    audio_file = models.FileField(upload_to="patient_notes/audio/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.language})"
