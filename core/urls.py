from django.contrib import admin
from django.urls import path, include
from patients.views import dashboard
from patient_activity.views import patient_logs
from django.contrib.auth import views as auth_views  

# Import JWT views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard),  # homepage
    path('dashboard/', dashboard),
    path('api/', include('patients.urls')),
    path('api/patient-logs/', patient_logs),
    path('accounts/', include('django.contrib.auth.urls')),

    # JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
