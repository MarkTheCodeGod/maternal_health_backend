# Voice Maternal Health CMS and Analytics

##  Project Overview
This project delivers a backend **Content Management System (CMS)** and **analytics framework** for a voice‑based maternal health information platform. It empowers healthcare providers to upload, organize, and deliver multilingual health education materials (text, audio) while tracking user engagement through analytics.

Developed as a final year project at the University of Zambia, the system addresses barriers of literacy, language diversity, and access to healthcare by enabling **voice‑enabled maternal health education**.

---

##  Objectives
- Develop a CMS for uploading and organizing maternal health content by pregnancy stage, topic, and language.
- Implement a REST API to serve content to mobile apps or voice engines.
- Integrate analytics to track content access and user engagement.
- Build an admin dashboard for content management and visualization.
- Provide technical documentation and evaluation.

---

## Features
- **JWT Authentication** for secure API access.
- **Role‑based dashboards** (Admin, Editor, Viewer) with permission‑restricted CRUD views.
- **Multilingual content support** with audio uploads stored in Django `MEDIA_ROOT`.
- **REST API endpoints** tested with Postman for seamless integration.
- **Analytics dashboard** using Chart.js for engagement visualization.
- **Activity logging** for monitoring usage patterns.

---

## Tech Stack
- **Backend:** Django, Django REST Framework  
- **Database:** PostgreSQL  
- **Frontend:** HTML, CSS, JavaScript, Chart.js  
- **Storage:** Local media folder (with option for cloud storage)  
- **Testing:** Postman, Django unit tests  
- **Version Control:** GitHub  

---

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd maternal_health_cms
