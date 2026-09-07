from django.urls import path
from .views import (
    PatientListCreateView,
    PatientRetrieveUpdateDeleteView,
    dashboard
)

urlpatterns = [
    # Handles GET (list) and POST (create)
    path('patients/', PatientListCreateView.as_view(), name='patient-list'),

    # Handles GET (single), PUT (update), DELETE (remove)
    path('patients/<int:pk>/', PatientRetrieveUpdateDeleteView.as_view(), name='patient-detail'),

    # Dashboard route
    path('dashboard/', dashboard, name='dashboard'),
]
