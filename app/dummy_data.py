from __future__ import annotations

from datetime import datetime

DUMMY_DATA = {
    "users": [
        {"id": 1, "name": "Admin User", "email": "admin@learnhub.com", "password": "admin123", "role": "admin"},
        {"id": 2, "name": "Priya Mentor", "email": "priya@learnhub.com", "password": "mentor123", "role": "mentor"},
        {"id": 3, "name": "Arjun Mentee", "email": "arjun@learnhub.com", "password": "mentee123", "role": "mentee"},
    ],
    "courses": [
        {
            "id": 1,
            "title": "Intro to Algebra",
            "subject": "Mathematics",
            "description": "Foundations of algebra for beginners.",
            "mentor_id": 2,
            "difficulty": "beginner",
            "rating": 4.5,
            "status": "approved",
            "created_at": datetime(2025, 1, 10, 9, 0, 0),
            "updated_at": datetime(2025, 1, 12, 9, 0, 0),
            "modules": [
                {
                    "id": 1,
                    "title": "Variables & Expressions",
                    "lectures": [
                        {
                            "id": 1,
                            "title": "What is a Variable?",
                            "video_url": "https://videos.learnhub.dev/algebra/variables",
                            "duration_minutes": 18,
                        },
                        {
                            "id": 2,
                            "title": "Writing Expressions",
                            "video_url": "https://videos.learnhub.dev/algebra/expressions",
                            "duration_minutes": 22,
                        },
                    ],
                    "assignments": [
                        {
                            "id": 1,
                            "title": "Variables Checkpoint",
                            "questions": [
                                {
                                    "id": 1,
                                    "prompt": "Which symbol commonly represents an unknown number?",
                                    "options": [
                                        {"text": "x", "is_correct": True},
                                        {"text": "=", "is_correct": False},
                                        {"text": "+", "is_correct": False},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ],
    "enrollments": [
        {"id": 1, "course_id": 1, "mentee_id": 3, "enrolled_at": datetime(2025, 1, 15, 9, 0, 0)}
    ],
    "progress": [
        {"enrollment_id": 1, "completed_lecture_ids": [1]}
    ],
}
