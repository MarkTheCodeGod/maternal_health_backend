from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Patient, Content

# 1x1 valid GIF byte string to pass image format validation
TINY_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
    b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
    b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
    b'\x44\x01\x00\x3b'
)


class PatientAPITests(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )

        self.normal_user = User.objects.create_user(
            username="user",
            password="user123"
        )

        self.patient = Patient.objects.create(
            name="Mary",
            age=25,
            stage="Second Trimester",
            notes="Test patient"
        )

    def test_anonymous_user_denied(self):
        response = self.client.get("/api/patients/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_user_can_view_patients(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.get("/api/patients/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_normal_user_cannot_delete_patient(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.delete(
            f"/api/patients/{self.patient.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_staff_user_can_delete_patient(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.delete(
            f"/api/patients/{self.patient.id}/"
        )

        self.assertIn(
            response.status_code,
            [200, 204]
        )


class ContentAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="contentuser",
            password="password123"
        )

    def test_anonymous_content_request_denied(self):
        """Anonymous access to /api/contents/ must return 401."""
        response = self.client.get("/api/contents/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_content_upload_retrieval_and_filtering(self):
        """Upload content with audio, image, text, stage, topic, and language, and filter."""
        self.client.force_authenticate(user=self.user)

        audio_file = SimpleUploadedFile("advice.mp3", b"dummy audio", content_type="audio/mpeg")
        image_file = SimpleUploadedFile("diagram.gif", TINY_GIF, content_type="image/gif")

        # 1. Upload content
        payload = {
            'title': 'Nutrition Guide',
            'stage': 'First Trimester',
            'topic': 'Nutrition',
            'language': 'en',
            'notes': 'Eat leafy greens and stay hydrated.',
            'audio_file': audio_file,
            'image_file': image_file,
        }

        response = self.client.post('/api/contents/', payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        content_id = response.data['id']

        # 2. Retrieve content
        get_res = self.client.get(f'/api/contents/{content_id}/')
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data['topic'], 'Nutrition')
        self.assertEqual(get_res.data['stage'], 'First Trimester')

        # 3. Filter by matching language and topic
        filter_res = self.client.get('/api/contents/?language=en&topic=Nutrition')
        self.assertEqual(filter_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(filter_res.data), 1)

        # 4. Filter by non-matching language returns empty list
        filter_empty = self.client.get('/api/contents/?language=es')
        self.assertEqual(len(filter_empty.data), 0)

    def test_language_linkage(self):
        """Test linking different language versions through translation_of."""
        self.client.force_authenticate(user=self.user)

        # Base English content
        base_item = Content.objects.create(
            title='Exercise Guide',
            stage='Second Trimester',
            topic='Fitness',
            language='en',
            notes='Moderate walking recommended.'
        )

        # Linked French translation
        payload = {
            'title': "Guide d'exercice",
            'stage': 'Second Trimester',
            'topic': 'Fitness',
            'language': 'fr',
            'notes': 'Marche modérée recommandée.',
            'translation_of': base_item.id
        }

        response = self.client.post('/api/contents/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['translation_of'], base_item.id)