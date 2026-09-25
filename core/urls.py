from django.contrib import admin
from django.urls import path, include
from patients.views import dashboard
from patient_activity.views import patient_logs
from django.contrib.auth import views as auth_views  

#  Import JWT views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard),  # homepage
    path('dashboard/', dashboard),
    path('api/', include('patients.urls')),
    path('api/patient-logs/', patient_logs),
    path('accounts/', include('django.contrib.auth.urls')),

    #  JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
