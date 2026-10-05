from rest_framework import serializers
from .models import Patient, Content

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'age', 'stage', 'notes']


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            'id', 
            'patient', 
            'title', 
            'stage', 
            'topic', 
            'language', 
            'notes', 
            'audio_file', 
            'image_file', 
            'translation_of', 
            'created_at'
        ]
        extra_kwargs = {
            # Allows content to be created without forcing a patient
            'patient': {'required': False, 'allow_null': True},
        }