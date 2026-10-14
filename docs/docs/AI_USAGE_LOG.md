# AI Usage Logbook and Verification Protocol

In accordance with institutional guidelines, artificial intelligence tools (Claude, ChatGPT, and Gemini) were utilized during development for scaffolding, syntax guidance, and test design. All AI outputs were reviewed, modified, and verified by the author.

| Phase / Task | AI Tool & Version | Nature of Assistance | Verification and Quality Control Protocol |
| :--- | :--- | :--- | :--- |
| **Schema Design & ForeignKey Rules** | Claude 3.5 Sonnet | Suggested syntax for self-referencing foreign keys (`translation_of`) and resolving cascade deletion defects (`models.SET_NULL`). | Inspected Django migration files; verified constraints directly in PostgreSQL via `psql`. |
| **Role-Based Access Migration** | Gemini 1.5 Pro | Scaffolded data migration to create Admin, Editor, and Viewer groups. | Discovered permissions were empty on fresh DB; updated migration to resolve model permissions explicitly. Verified counts via Django shell (16/12/4). |
| **RBAC API Enforcement** | ChatGPT (GPT-4o) | Suggested scaffolding custom permission classes for viewsets. | Implemented custom `PatientPermission` and `ContentPermission` classes in `patients/views.py`. Tested directly via `APITestCase` asserting HTTP 403. |
| **Automated Test Suite** | Claude 3.5 Sonnet | Generated boilerplate structure for `APITestCase` methods and 1x1 GIF mock image byte strings. | Reviewed test code, corrected URL routes to `/api/contents/`, and executed suite via `python manage.py test` (13 passing tests). |
| **Latency Benchmark Harness** | Claude 3.5 Sonnet | Scaffolded in-process timing script using `time.perf_counter()` and DRF `APIClient`. | Executed benchmark across 80 samples against PostgreSQL and committed raw output to `docs/latency_benchmark.txt`. |
| **Repository Sanitization** | ChatGPT (GPT-4o) | Formulated Git commands to purge untracked media and rebuild clean Git history. | Verified clean Git history and confirmed untracked media directories. |