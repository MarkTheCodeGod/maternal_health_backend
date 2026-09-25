from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard, add_patient, view_patient, update_patient, delete_patient,
    PatientListCreateView, PatientRetrieveUpdateDeleteView, ContentViewSet
)

router = DefaultRouter()
router.register(r'contents', ContentViewSet, basename='contents')

urlpatterns = [
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),

    # HTML views (form-based CRUD)
    path('add_patient/', add_patient, name='add_patient'),
    path('view_patient/', view_patient, name='view_patient'),
    path('update_patient/<int:pk>/', update_patient, name='update_patient'),
    path('delete_patient/<int:pk>/', delete_patient, name='delete_patient'),

    # API endpoints (Postman / external clients)
    path('patients/', PatientListCreateView.as_view(), name='patients_list_create'),
    path('patients/<int:pk>/', PatientRetrieveUpdateDeleteView.as_view(), name='patients_detail'),
]

urlpatterns += router.urls
