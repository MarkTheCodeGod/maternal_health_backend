from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PatientActivityLog


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_logs(request):
    logs = PatientActivityLog.objects.all().order_by('-timestamp')
    data = [
        {
            "id": log.id,
            "action": log.action,
            "patient_identifier": log.patient_identifier or (log.patient.name if log.patient else "Deleted Patient"),
            "user": log.user.username if log.user else None,
            "role": log.role or "Unassigned",
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]
    return Response(data)