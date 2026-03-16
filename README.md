# LearnHub API

Python FastAPI backend for the LearnHub EdTech platform.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

## Demo credentials

- Admin: `admin@learnhub.com` / `admin123`
- Mentor: `priya@learnhub.com` / `mentor123`
- Mentee: `arjun@learnhub.com` / `mentee123`

## Core endpoints

- `POST /auth/login`
- `GET /users/me`
- `POST /courses` (mentor)
- `POST /courses/{id}/submit` (mentor)
- `POST /courses/{id}/approve` and `/reject` (admin)
- `GET /courses` (search/filter with `subject`, `difficulty`, `min_rating`, `mentor_id`, `q`)
- `POST /enrollments` (mentee)
- `GET /enrollments/{id}/progress` (mentee)
