"""
Latency Benchmark Script for Maternal Health CMS API
Measures response latency across authenticated endpoints and exports statistics.
"""
import os
import time
import django
import statistics

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient

def run_benchmark():
    print("=" * 60)
    print("Maternal Health CMS - API Latency Measurement Benchmark")
    print("=" * 60)

    # Setup client and test user
    client = APIClient()
    user, _ = User.objects.get_or_create(username='benchmark_user')
    user.set_password('benchpass123')
    user.save()
    client.force_authenticate(user=user)

    endpoints = [
        ("GET /api/patients/", "/api/patients/"),
        ("GET /api/contents/", "/api/contents/"),
        ("GET /api/patient-logs/", "/api/patient-logs/"),
        ("GET /api/contents/?language=en", "/api/contents/?language=en"),
    ]

    iterations = 20
    results_summary = []
    output_lines = []

    header = f"API Latency Benchmark Run ({iterations} iterations per endpoint)\n"
    header += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += "-" * 60 + "\n"
    print(header)
    output_lines.append(header)

    all_durations = []

    for name, url in endpoints:
        durations = []
        # Warmup request
        client.get(url)

        for _ in range(iterations):
            start = time.perf_counter()
            response = client.get(url)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            durations.append(elapsed_ms)
            all_durations.append(elapsed_ms)

        mean_ms = statistics.mean(durations)
        min_ms = min(durations)
        max_ms = max(durations)
        stdev_ms = statistics.stdev(durations) if len(durations) > 1 else 0.0

        summary = (
            f"Endpoint: {name}\n"
            f"  Samples: {iterations}\n"
            f"  Mean Latency: {mean_ms:.2f} ms\n"
            f"  Min / Max: {min_ms:.2f} ms / {max_ms:.2f} ms\n"
            f"  Std Dev: {stdev_ms:.2f} ms\n"
        )
        print(summary)
        output_lines.append(summary)

    overall_mean = statistics.mean(all_durations)
    overall_min = min(all_durations)
    overall_max = max(all_durations)
    overall_summary = (
        "=" * 60 + "\n"
        f"OVERALL ACROSS ALL ENDPOINTS ({len(all_durations)} samples):\n"
        f"  Mean Latency: {overall_mean:.2f} ms\n"
        f"  Observed Range (Min - Max): {overall_min:.2f} ms - {overall_max:.2f} ms\n"
        "=" * 60 + "\n"
    )
    print(overall_summary)
    output_lines.append(overall_summary)

    # Save to docs/latency_benchmark.txt
    os.makedirs('docs', exist_ok=True)
    with open('docs/latency_benchmark.txt', 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print("Results successfully saved to docs/latency_benchmark.txt!")

if __name__ == '__main__':
    run_benchmark()