from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    stage = models.CharField(max_length=50)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
