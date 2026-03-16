from __future__ import annotations

from typing import List, TypedDict


class OptionSeed(TypedDict):
    text: str
    is_correct: bool


class QuestionSeed(TypedDict):
    id: int
    prompt: str
    options: List[OptionSeed]


class AssignmentSeed(TypedDict):
    id: int
    title: str
    questions: List[QuestionSeed]


class LectureSeed(TypedDict):
    id: int
    title: str
    video_url: str
    duration_minutes: int


class ModuleSeed(TypedDict):
    id: int
    title: str
    lectures: List[LectureSeed]
    assignments: List[AssignmentSeed]


class CourseSeed(TypedDict):
    id: int
    title: str
    subject: str
    description: str
    mentor_id: int
    difficulty: str
    rating: float
    status: str
    modules: List[ModuleSeed]


class UserSeed(TypedDict):
    id: int
    name: str
    email: str
    password: str
    role: str


class EnrollmentSeed(TypedDict):
    id: int
    course_id: int
    mentee_id: int
    completed_lecture_ids: List[int]
