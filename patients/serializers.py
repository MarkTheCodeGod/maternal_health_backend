from rest_framework import serializers
from .models import Patient, Content

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'age', 'stage', 'notes']


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'patient', 'title', 'topic', 'language', 'notes', 'audio_file', 'created_at']
