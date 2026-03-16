from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_mentor_to_admin_to_mentee_flow():
    mentor_token = login("priya@learnhub.com", "mentor123")
    admin_token = login("admin@learnhub.com", "admin123")
    mentee_token = login("arjun@learnhub.com", "mentee123")

    course = client.post(
        "/courses",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={
            "title": "Physics 101",
            "subject": "Physics",
            "description": "Foundations",
            "difficulty": "beginner",
        },
    )
    assert course.status_code == 201
    course_id = course.json()["id"]

    module = client.post(
        f"/courses/{course_id}/modules",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"title": "Mechanics"},
    )
    assert module.status_code == 200
    module_id = module.json()["modules"][0]["id"]

    lecture = client.post(
        f"/courses/{course_id}/modules/{module_id}/lectures",
        headers={"Authorization": f"Bearer {mentor_token}"},
        json={"title": "Newton Laws", "video_url": "https://video", "duration_minutes": 20},
    )
    assert lecture.status_code == 200
    lecture_id = lecture.json()["modules"][0]["lectures"][0]["id"]

    submit = client.post(f"/courses/{course_id}/submit", headers={"Authorization": f"Bearer {mentor_token}"})
    assert submit.status_code == 200
    assert submit.json()["status"] == "pending"

    approve = client.post(f"/courses/{course_id}/approve", headers={"Authorization": f"Bearer {admin_token}"})
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    catalog = client.get("/courses", headers={"Authorization": f"Bearer {mentee_token}"})
    assert catalog.status_code == 200
    assert any(item["id"] == course_id for item in catalog.json())

    enrollment = client.post(
        "/enrollments",
        headers={"Authorization": f"Bearer {mentee_token}"},
        json={"course_id": course_id},
    )
    assert enrollment.status_code == 201
    enrollment_id = enrollment.json()["id"]

    complete = client.post(
        f"/enrollments/{enrollment_id}/lectures/{lecture_id}/complete",
        headers={"Authorization": f"Bearer {mentee_token}"},
    )
    assert complete.status_code == 200
    assert complete.json()["completion_percentage"] == 100.0
