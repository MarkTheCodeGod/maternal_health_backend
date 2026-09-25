from django.contrib import admin
from django.urls import path, include
from patients.views import dashboard
from patient_activity.views import patient_logs
from django.contrib.auth import views as auth_views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard),  # homepage
    path('dashboard/', dashboard),
    path('', include('patients.urls')),
    path('api/patient-logs/', patient_logs),
    path('accounts/', include('django.contrib.auth.urls')),  
]
