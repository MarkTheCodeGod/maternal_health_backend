# Voice Maternal Health CMS and Backend API

A secure, decoupled Content Management System (CMS) and REST API framework for voice-oriented maternal health education and patient tracking in low-resource environments.

## System Features
- **Trimester-Staged Content Management:** Organizes guidance by clinical gestational stages (First Trimester, Second Trimester, Third Trimester, Postnatal), health topics, and languages in text, MP3 audio, and anatomical image formats.
- **Multilingual Translation Linkage:** Self-referencing foreign key (`translation_of`) links vernacular translations directly to base clinical guidance.
- **Role-Based Access Control (RBAC):** Group permissions populated upon migration (`Admin` 16, `Editor` 12, `Viewer` 4 permissions), enforced via custom DRF permission classes (`PatientPermission` and `ContentPermission`).
- **Non-Destructive Audit Logging:** Synchronous audit trail in `PatientActivityLog` capturing actor (`user`), executing `role`, action, and persistent `patient_identifier`, retained upon deletion via `models.SET_NULL`.
- **Stateless JWT Authentication:** SimpleJWT token verification protecting clinical endpoints.

## Verification & Automated Testing
The system contains an automated test suite of 13 regression tests across two test classes:
```bash
python manage.py test