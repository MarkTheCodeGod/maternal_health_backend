from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PatientActivityLog

@api_view(['GET'])
def patient_logs(request):
    logs = PatientActivityLog.objects.all().order_by('-timestamp')
    data = [
        {"action": log.action, "timestamp": log.timestamp}
        for log in logs
    ]
    return Response(data)
