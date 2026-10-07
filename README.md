# Maternal Health Educational Content Management System (Backend Prototype)

A robust Django & Django REST Framework backend prototype for managing multilingual, staged maternal health educational content and patient activity auditing.

## Overview
This system provides a secure, role-governed REST API and administrative interface for managing maternal health educational resources across trimesters and local languages (e.g., English, Bemba, Nyanja). The architecture preserves administrative activity logs and content independently of patient record lifecycles.

## Features
- **Trimester-Staged & Multilingual Content:** Supports text, audio, and visual health materials linked across translations (`translation_of`).
- **Role-Based Access Control (RBAC):**
  - **Admin:** Full CRUD access and administrative deletion.
  - **Editor:** Create and update content and patient records.
  - **Viewer:** Strict read-only access (all write requests refused with HTTP 403 Forbidden).
- **Referential Integrity & Audit Logging:** Deleting a patient retains administrative audit trail rows in `PatientActivityLog` with stable patient identifiers and user/role attribution (`models.SET_NULL`).
- **Query Filtering:** Case-insensitive filtering on `/api/contents/` by `stage`, `topic`, and `language`.
- **Automated Verification:** 13 committed Django REST Framework API test cases covering authentication, role permissions, filtering, and audit log persistence.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL or SQLite3

### 2. Clone and Setup Environment
```bash
git clone <repository-url>
cd maternal_health_cms

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate