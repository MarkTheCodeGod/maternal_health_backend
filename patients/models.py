from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    stage = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Content(models.Model):
    # 1. Content is no longer strictly tied to a patient; deleting a patient won't wipe content
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="contents"
    )
    title = models.CharField(max_length=255)
    
    # 2. Stage added (e.g., First Trimester, Second Trimester, Postnatal)
    stage = models.CharField(max_length=100, blank=True)
    topic = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    
    # 3. Formats: Text, Audio, and Image
    notes = models.TextField(blank=True)  # Text content
    audio_file = models.FileField(upload_to="patient_notes/audio/", null=True, blank=True)
    image_file = models.ImageField(upload_to="patient_notes/images/", null=True, blank=True)
    
    # 4. Language linkage: links a translation to its original base content
    translation_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="translations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.language}) - {self.stage}"