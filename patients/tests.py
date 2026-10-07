from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Patient, Content
from patient_activity.models import PatientActivityLog

# 1x1 valid GIF byte string to pass image format validation
TINY_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
    b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
    b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
    b'\x44\x01\x00\x3b'
)


class PatientAPITests(APITestCase):

    def setUp(self):
        # Create groups
        self.admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.editor_group, _ = Group.objects.get_or_create(name='Editor')
        self.viewer_group, _ = Group.objects.get_or_create(name='Viewer')

        # Admin user
        self.staff_user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        self.staff_user.groups.add(self.admin_group)

        # Editor user
        self.editor_user = User.objects.create_user(
            username="editor",
            password="editor123"
        )
        self.editor_user.groups.add(self.editor_group)

        # Viewer user
        self.viewer_user = User.objects.create_user(
            username="viewer",
            password="viewer123"
        )
        self.viewer_user.groups.add(self.viewer_group)

        # Normal user without role
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
        self.client.force_authenticate(user=self.viewer_user)
        response = self.client.get("/api/patients/")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_viewer_cannot_create_patient(self):
        """Viewer role must receive 403 Forbidden on POST."""
        self.client.force_authenticate(user=self.viewer_user)
        payload = {"name": "Jane", "age": 28, "stage": "First Trimester", "notes": "New"}
        response = self.client.post("/api/patients/", payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_update_patient(self):
        """Viewer role must receive 403 Forbidden on PUT/PATCH."""
        self.client.force_authenticate(user=self.viewer_user)
        payload = {"name": "Mary Updated", "age": 26, "stage": "Second Trimester", "notes": "Updated"}
        response = self.client.put(f"/api/patients/{self.patient.id}/", payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_create_and_update_patient(self):
        """Editor role can POST and PUT patients."""
        self.client.force_authenticate(user=self.editor_user)
        # Create
        create_payload = {"name": "Sarah", "age": 30, "stage": "First Trimester", "notes": "Editor created"}
        res_create = self.client.post("/api/patients/", create_payload)
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        new_id = res_create.data['id']

        # Update
        update_payload = {"name": "Sarah Revised", "age": 31, "stage": "First Trimester", "notes": "Editor updated"}
        res_update = self.client.put(f"/api/patients/{new_id}/", update_payload)
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)

    def test_editor_cannot_delete_patient(self):
        """Editor role must receive 403 Forbidden on DELETE."""
        self.client.force_authenticate(user=self.editor_user)
        response = self.client.delete(f"/api/patients/{self.patient.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_delete_patient(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(f"/api/patients/{self.patient.id}/")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_staff_user_can_delete_patient(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(f"/api/patients/{self.patient.id}/")
        self.assertIn(response.status_code, [200, 204])

    def test_audit_log_records_user_and_role_on_delete(self):
        """Verify PatientActivityLog records who deleted the patient and their role."""
        self.client.force_authenticate(user=self.staff_user)
        self.client.delete(f"/api/patients/{self.patient.id}/")

        log = PatientActivityLog.objects.filter(action='deleted').last()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.staff_user)
        self.assertEqual(log.role, 'Admin')


class ContentAPITests(APITestCase):

    def setUp(self):
        self.editor_group, _ = Group.objects.get_or_create(name='Editor')
        self.viewer_group, _ = Group.objects.get_or_create(name='Viewer')

        # Editor user for uploading content
        self.user = User.objects.create_user(
            username="contentuser",
            password="password123"
        )
        self.user.groups.add(self.editor_group)

        # Viewer user
        self.viewer_user = User.objects.create_user(
            username="vieweruser",
            password="password123"
        )
        self.viewer_user.groups.add(self.viewer_group)

    def test_anonymous_content_request_denied(self):
        """Anonymous access to /api/contents/ must return 401."""
        response = self.client.get("/api/contents/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewer_cannot_upload_content(self):
        """Viewer role must receive 403 Forbidden when creating content."""
        self.client.force_authenticate(user=self.viewer_user)
        payload = {
            'title': 'Forbidden Guide',
            'stage': 'First Trimester',
            'topic': 'Health',
            'language': 'en',
            'notes': 'Viewer attempting upload.'
        }
        response = self.client.post('/api/contents/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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