from django.contrib import admin
from django.urls import path, include
from patients.views import dashboard
from patient_activity.views import patient_logs
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard),
    path('api/', include('patients.urls')),          # patients API routes
    path('api/patient-logs/', patient_logs),         # patient activity logs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
