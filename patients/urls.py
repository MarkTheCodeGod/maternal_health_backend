from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # HTML views (form-based CRUD)
    path('add_patient/', views.add_patient, name='add_patient'),
    path('view_patient/', views.view_patient, name='view_patient'),
    path('update_patient/<int:pk>/', views.update_patient, name='update_patient'),
    path('delete_patient/<int:pk>/', views.delete_patient, name='delete_patient'),

    # API endpoints (Postman / external clients)
    path('patients/', views.PatientListCreateView.as_view(), name='patients_list_create'),
    path('patients/<int:pk>/', views.PatientRetrieveUpdateDeleteView.as_view(), name='patients_detail'),
]
