from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    stage = models.CharField(max_length=50)  # e.g. First Trimester, Second Trimester
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Content(models.Model):
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100)  # e.g. Nutrition, Antenatal Care
    language = models.CharField(max_length=50)  # e.g. English, Bemba, Nyanja
    file_path = models.FileField(upload_to='content_files/')
    linked_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="contents")

    def __str__(self):
        return f"{self.title} ({self.language})"
