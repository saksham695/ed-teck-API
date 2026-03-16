from __future__ import annotations

from typing import Any, Dict, Iterable, List, Type


def build_users(raw_users: Iterable[dict[str, Any]], user_model: Type[Any], role_enum: Type[Any]) -> Dict[int, Any]:
    users: Dict[int, Any] = {}
    for data in raw_users:
        user = user_model(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            password=data["password"],
            role=role_enum(data["role"]),
        )
        users[user.id] = user
    return users


def build_courses(
    raw_courses: Iterable[dict[str, Any]],
    *,
    course_model: Type[Any],
    module_model: Type[Any],
    lecture_model: Type[Any],
    assignment_model: Type[Any],
    question_model: Type[Any],
    option_model: Type[Any],
    difficulty_enum: Type[Any],
    status_enum: Type[Any],
) -> Dict[int, Any]:
    courses: Dict[int, Any] = {}

    for data in raw_courses:
        modules: List[Any] = []
        for module_data in data["modules"]:
            lectures = [lecture_model(**lecture_data) for lecture_data in module_data["lectures"]]

            assignments = []
            for assignment_data in module_data["assignments"]:
                questions = []
                for question_data in assignment_data["questions"]:
                    options = [option_model(**option_data) for option_data in question_data["options"]]
                    questions.append(
                        question_model(
                            id=question_data["id"],
                            prompt=question_data["prompt"],
                            options=options,
                        )
                    )
                assignments.append(
                    assignment_model(
                        id=assignment_data["id"],
                        title=assignment_data["title"],
                        questions=questions,
                    )
                )

            modules.append(
                module_model(
                    id=module_data["id"],
                    title=module_data["title"],
                    lectures=lectures,
                    assignments=assignments,
                )
            )

        course = course_model(
            id=data["id"],
            title=data["title"],
            subject=data["subject"],
            description=data["description"],
            mentor_id=data["mentor_id"],
            difficulty=difficulty_enum(data["difficulty"]),
            rating=data["rating"],
            status=status_enum(data["status"]),
            modules=modules,
        )
        courses[course.id] = course

    return courses


def build_enrollments(
    raw_enrollments: Iterable[dict[str, Any]],
    *,
    enrollment_model: Type[Any],
    progress_model: Type[Any],
) -> tuple[Dict[int, Any], Dict[int, Any]]:
    enrollments: Dict[int, Any] = {}
    progress: Dict[int, Any] = {}

    for data in raw_enrollments:
        enrollment = enrollment_model(
            id=data["id"],
            course_id=data["course_id"],
            mentee_id=data["mentee_id"],
        )
        enrollments[enrollment.id] = enrollment
        progress[enrollment.id] = progress_model(
            enrollment_id=enrollment.id,
            completed_lecture_ids=data["completed_lecture_ids"],
        )

    return enrollments, progress


def calculate_next_ids(courses: Iterable[Any], enrollments: Iterable[Any]) -> dict[str, int]:
    course_list = list(courses)
    enrollment_list = list(enrollments)

    return {
        "course": max([course.id for course in course_list], default=0) + 1,
        "module": max([module.id for course in course_list for module in course.modules], default=0) + 1,
        "lecture": max(
            [lecture.id for course in course_list for module in course.modules for lecture in module.lectures],
            default=0,
        )
        + 1,
        "assignment": max(
            [assignment.id for course in course_list for module in course.modules for assignment in module.assignments],
            default=0,
        )
        + 1,
        "question": max(
            [
                question.id
                for course in course_list
                for module in course.modules
                for assignment in module.assignments
                for question in assignment.questions
            ],
            default=0,
        )
        + 1,
        "enrollment": max([enrollment.id for enrollment in enrollment_list], default=0) + 1,
    }
