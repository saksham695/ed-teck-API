from __future__ import annotations

from app.data_contracts import CourseSeed, EnrollmentSeed, UserSeed

DUMMY_USERS: list[UserSeed] = [
    {
        "id": 1,
        "name": "Admin User",
        "email": "admin@learnhub.com",
        "password": "admin123",
        "role": "admin",
    },
    {
        "id": 2,
        "name": "Priya Mentor",
        "email": "priya@learnhub.com",
        "password": "mentor123",
        "role": "mentor",
    },
    {
        "id": 3,
        "name": "Arjun Mentee",
        "email": "arjun@learnhub.com",
        "password": "mentee123",
        "role": "mentee",
    },
    {
        "id": 4,
        "name": "Nina Mentor",
        "email": "nina@learnhub.com",
        "password": "mentor123",
        "role": "mentor",
    },
]

DUMMY_COURSES: list[CourseSeed] = [
    {
        "id": 1,
        "title": "Python Fundamentals",
        "subject": "Computer Science",
        "description": "A beginner friendly Python bootcamp.",
        "mentor_id": 2,
        "difficulty": "beginner",
        "rating": 4.6,
        "status": "approved",
        "modules": [
            {
                "id": 1,
                "title": "Getting Started",
                "lectures": [
                    {
                        "id": 1,
                        "title": "Setup and Tools",
                        "video_url": "https://video.example.com/python/setup",
                        "duration_minutes": 12,
                    },
                    {
                        "id": 2,
                        "title": "Variables and Types",
                        "video_url": "https://video.example.com/python/variables",
                        "duration_minutes": 18,
                    },
                ],
                "assignments": [
                    {
                        "id": 1,
                        "title": "Python Basics Quiz",
                        "questions": [
                            {
                                "id": 1,
                                "prompt": "Which type stores text in Python?",
                                "options": [
                                    {"text": "str", "is_correct": True},
                                    {"text": "int", "is_correct": False},
                                    {"text": "bool", "is_correct": False},
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    },
    {
        "id": 2,
        "title": "Advanced SQL Patterns",
        "subject": "Databases",
        "description": "Performance-focused SQL for experienced developers.",
        "mentor_id": 4,
        "difficulty": "advanced",
        "rating": 4.2,
        "status": "pending",
        "modules": [],
    },
]

DUMMY_ENROLLMENTS: list[EnrollmentSeed] = [
    {
        "id": 1,
        "course_id": 1,
        "mentee_id": 3,
        "completed_lecture_ids": [1],
    }
]
