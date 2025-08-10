# jobboard-backend# Job Board API

A Flask-based REST API for a job board application supporting two user roles: **Applicants** and **Companies**.  
Applicants can register, verify email, login, view jobs, and apply. Companies can register, verify email, login, post jobs, and manage applications.

---

## Features Implemented

### Authentication

- User registration with email verification (token-based)
- User login with JWT authentication
- Protected routes with JWT
- User roles: `applicant` and `company`
- Role-based access control decorator (`role_required`)
- Get current logged-in user profile endpoint

### Jobs

- Companies can create, update, delete jobs
- List all jobs with optional status filter (`draft`, `open`, `closed`)
- Get job details by ID

### Applications

- Applicants can apply to jobs with resume link and cover letter
- Applicants can withdraw applications
- Companies can view applications for their jobs
- Companies can update application status (`applied`, `reviewed`, `interview`, `rejected`, `hired`)

---

## API Endpoints

### Auth

| Endpoint                         | Method | Description                         |
| -------------------------------- | ------ | ----------------------------------- |
| `/api/auth/register`             | POST   | Register a new user                 |
| `/api/auth/verify-email/<token>` | GET    | Verify user email via token         |
| `/api/auth/login`                | POST   | Login and get JWT token             |
| `/api/auth/me`                   | GET    | Get profile of logged-in user (JWT) |

### Jobs

| Endpoint             | Method | Description                        |
| -------------------- | ------ | ---------------------------------- |
| `/api/jobs`          | GET    | List jobs (optional status filter) |
| `/api/jobs`          | POST   | Create a job (company role only)   |
| `/api/jobs/<job_id>` | GET    | Get job details                    |
| `/api/jobs/<job_id>` | PUT    | Update job (company role only)     |
| `/api/jobs/<job_id>` | DELETE | Delete job (company role only)     |

### Applications

| Endpoint                         | Method | Description                           |
| -------------------------------- | ------ | ------------------------------------- |
| `/api/applications`              | POST   | Apply to a job (applicant role only)  |
| `/api/applications/my`           | GET    | List applicant's applications         |
| `/api/applications/job/<job_id>` | GET    | List applications for a job (company) |
| `/api/applications/<id>`         | GET    | Get application details               |
| `/api/applications/<id>`         | PUT    | Update application status (company)   |
| `/api/applications/<id>`         | DELETE | Withdraw application (applicant)      |

---

## Technologies Used

- Python 3.11+
- Flask
- Flask-JWT-Extended (JWT auth)
- Flask-Mail (email verification)
- Flask-SQLAlchemy (ORM)
- Werkzeug (password hashing)

---

## How to Run

1. Create `.env` with your config (database URL, mail settings, secret keys).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   flask db upgrade # if using migrations, or
   python
   > > > from app.extensions import db
   > > > from app import create_app
   > > > app = create_app()
   > > > app.app_context().push()
   > > > db.create_all()
   > > > flask run
