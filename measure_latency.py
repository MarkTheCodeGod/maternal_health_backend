import os
import sys
import time
import math
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from patients.models import Patient, Content
from patient_activity.models import PatientActivityLog

def run_benchmark():
    print("=" * 60)
    print("Maternal Health CMS - API Latency Measurement Benchmark")
    print("=" * 60)

    # Ensure clean test user
    user, _ = User.objects.get_or_create(username='benchmark_admin', defaults={'is_staff': True})
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    user.groups.add(admin_group)

    # Seed baseline records if empty
    if not Patient.objects.exists():
        p = Patient.objects.create(name="Benchmark Mother", age=24, stage="First Trimester", notes="Baseline")
        PatientActivityLog.objects.create(patient=p, patient_identifier=f"Patient #{p.id}: {p.name}", user=user, role="Admin", action="created")

    if not Content.objects.exists():
        Content.objects.create(title="Benchmark Nutrition", stage="First Trimester", topic="Nutrition", language="en", notes="Folic acid guidance")

    client = APIClient()
    client.force_authenticate(user=user)

    endpoints = [
        ('GET', '/api/contents/'),
        ('GET', '/api/patients/'),
        ('GET', '/api/patient-logs/'),
        ('GET', '/api/contents/?language=en'),
    ]

    results_file = os.path.join('docs', 'latency_benchmark.txt')
    os.makedirs('docs', exist_ok=True)

    lines = []
    lines.append("=" * 60)
    lines.append("Maternal Health CMS - API Latency Measurement Benchmark")
    lines.append("=" * 60)

    all_latencies = []

    for method, url in endpoints:
        durations = []
        # 20 iterations
        for _ in range(20):
            t0 = time.perf_counter()
            response = client.get(url)
            t1 = time.perf_counter()
            duration_ms = (t1 - t0) * 1000.0
            durations.append(duration_ms)
            all_latencies.append(duration_ms)

        mean_ms = sum(durations) / len(durations)
        min_ms = min(durations)
        max_ms = max(durations)
        variance = sum((x - mean_ms) ** 2 for x in durations) / len(durations)
        std_dev_ms = math.sqrt(variance)

        endpoint_summary = (
            f"Endpoint: {method} {url}\n"
            f"  Samples: {len(durations)}\n"
            f"  Mean Latency: {mean_ms:.2f} ms\n"
            f"  Min / Max: {min_ms:.2f} ms / {max_ms:.2f} ms\n"
            f"  Std Dev: {std_dev_ms:.2f} ms\n"
        )
        print(endpoint_summary)
        lines.append(endpoint_summary)

    overall_mean = sum(all_latencies) / len(all_latencies)
    overall_min = min(all_latencies)
    overall_max = max(all_latencies)
    overall_variance = sum((x - overall_mean) ** 2 for x in all_latencies) / len(all_latencies)
    overall_std_dev = math.sqrt(overall_variance)

    separator = "=" * 60
    summary_block = (
        f"{separator}\n"
        f"OVERALL ACROSS ALL ENDPOINTS ({len(all_latencies)} samples):\n"
        f"  Mean Latency: {overall_mean:.2f} ms\n"
        f"  Observed Range (Min - Max): {overall_min:.2f} ms - {overall_max:.2f} ms\n"
        f"  Standard Deviation: {overall_std_dev:.2f} ms\n"
        f"{separator}\n"
    )
    print(summary_block)
    lines.append(summary_block)

    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"Results successfully saved to {results_file}!")

if __name__ == '__main__':
    run_benchmark()