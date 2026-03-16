from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field


app = FastAPI(title="LearnHub API", version="1.0.0")


class Role(str, Enum):
    admin = "admin"
    mentor = "mentor"
    mentee = "mentee"


class CourseStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str
    role: Role


class MCQOption(BaseModel):
    text: str
    is_correct: bool = False


class MCQQuestion(BaseModel):
    id: int
    prompt: str
    options: List[MCQOption] = Field(default_factory=list)


class Assignment(BaseModel):
    id: int
    title: str
    questions: List[MCQQuestion] = Field(default_factory=list)


class Lecture(BaseModel):
    id: int
    title: str
    video_url: str
    duration_minutes: int


class Module(BaseModel):
    id: int
    title: str
    lectures: List[Lecture] = Field(default_factory=list)
    assignments: List[Assignment] = Field(default_factory=list)


class Course(BaseModel):
    id: int
    title: str
    subject: str
    description: str
    mentor_id: int
    difficulty: Difficulty
    rating: float = 0.0
    status: CourseStatus = CourseStatus.draft
    modules: List[Module] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Enrollment(BaseModel):
    id: int
    course_id: int
    mentee_id: int
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)


class Progress(BaseModel):
    enrollment_id: int
    completed_lecture_ids: List[int] = Field(default_factory=list)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, str | int]


class CourseCreate(BaseModel):
    title: str
    subject: str
    description: str
    difficulty: Difficulty


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)


class ModuleCreate(BaseModel):
    title: str


class LectureCreate(BaseModel):
    title: str
    video_url: str
    duration_minutes: int = Field(gt=0)


class AssignmentCreate(BaseModel):
    title: str


class QuestionCreate(BaseModel):
    prompt: str
    options: List[MCQOption] = Field(default_factory=list)


class EnrollmentCreate(BaseModel):
    course_id: int


class Store:
    def __init__(self) -> None:
        self.users: Dict[int, User] = {}
        self.courses: Dict[int, Course] = {}
        self.enrollments: Dict[int, Enrollment] = {}
        self.progress: Dict[int, Progress] = {}
        self.tokens: Dict[str, int] = {}
        self._next_ids = {
            "course": 1,
            "module": 1,
            "lecture": 1,
            "assignment": 1,
            "question": 1,
            "enrollment": 1,
        }
        self._seed()

    def _seed(self) -> None:
        seeded = [
            User(id=1, name="Admin User", email="admin@learnhub.com", password="admin123", role=Role.admin),
            User(id=2, name="Priya Mentor", email="priya@learnhub.com", password="mentor123", role=Role.mentor),
            User(id=3, name="Arjun Mentee", email="arjun@learnhub.com", password="mentee123", role=Role.mentee),
        ]
        for user in seeded:
            self.users[user.id] = user

    def next_id(self, key: str) -> int:
        current = self._next_ids[key]
        self._next_ids[key] += 1
        return current


store = Store()


def get_current_user(authorization: str = Header(default="")) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = store.tokens.get(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return store.users[user_id]


def require_role(*roles: Role):
    def role_guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return role_guard


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = next((u for u in store.users.values() if u.email == payload.email and u.password == payload.password), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = str(uuid4())
    store.tokens[token] = user.id
    return LoginResponse(
        access_token=token,
        user={"id": user.id, "name": user.name, "email": user.email, "role": user.role},
    )


@app.get("/users/me")
def me(user: User = Depends(get_current_user)) -> Dict[str, str | int]:
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@app.post("/courses", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, mentor: User = Depends(require_role(Role.mentor))) -> Course:
    course = Course(
        id=store.next_id("course"),
        title=payload.title,
        subject=payload.subject,
        description=payload.description,
        mentor_id=mentor.id,
        difficulty=payload.difficulty,
    )
    store.courses[course.id] = course
    return course


@app.get("/courses", response_model=List[Course])
def list_courses(
    q: Optional[str] = Query(default=None),
    subject: Optional[str] = Query(default=None),
    difficulty: Optional[Difficulty] = Query(default=None),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    mentor_id: Optional[int] = Query(default=None),
    include_unapproved: bool = Query(default=False),
    user: Optional[User] = Depends(get_current_user),
) -> List[Course]:
    results = list(store.courses.values())

    if not include_unapproved or user.role != Role.admin:
        results = [c for c in results if c.status == CourseStatus.approved]

    if q:
        ql = q.lower()
        results = [c for c in results if ql in c.title.lower() or ql in c.description.lower()]
    if subject:
        results = [c for c in results if c.subject.lower() == subject.lower()]
    if difficulty:
        results = [c for c in results if c.difficulty == difficulty]
    if min_rating is not None:
        results = [c for c in results if c.rating >= min_rating]
    if mentor_id is not None:
        results = [c for c in results if c.mentor_id == mentor_id]

    return results


@app.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: int, user: User = Depends(get_current_user)) -> Course:
    course = store.courses.get(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.status != CourseStatus.approved and user.role not in {Role.admin} and user.id != course.mentor_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@app.patch("/courses/{course_id}", response_model=Course)
def update_course(course_id: int, payload: CourseUpdate, mentor: User = Depends(require_role(Role.mentor))) -> Course:
    course = store.courses.get(course_id)
    if not course or course.mentor_id != mentor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/modules", response_model=Course)
def add_module(course_id: int, payload: ModuleCreate, mentor: User = Depends(require_role(Role.mentor))) -> Course:
    course = store.courses.get(course_id)
    if not course or course.mentor_id != mentor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.modules.append(Module(id=store.next_id("module"), title=payload.title))
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/modules/{module_id}/lectures", response_model=Course)
def add_lecture(course_id: int, module_id: int, payload: LectureCreate, mentor: User = Depends(require_role(Role.mentor))) -> Course:
    course = store.courses.get(course_id)
    if not course or course.mentor_id != mentor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    module = next((m for m in course.modules if m.id == module_id), None)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    module.lectures.append(
        Lecture(
            id=store.next_id("lecture"),
            title=payload.title,
            video_url=payload.video_url,
            duration_minutes=payload.duration_minutes,
        )
    )
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/modules/{module_id}/assignments", response_model=Course)
def add_assignment(course_id: int, module_id: int, payload: AssignmentCreate, mentor: User = Depends(require_role(Role.mentor))) -> Course:
    course = store.courses.get(course_id)
    if not course or course.mentor_id != mentor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    module = next((m for m in course.modules if m.id == module_id), None)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    module.assignments.append(Assignment(id=store.next_id("assignment"), title=payload.title))
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/modules/{module_id}/assignments/{assignment_id}/questions", response_model=Course)
def add_question(
    course_id: int,
    module_id: int,
    assignment_id: int,
    payload: QuestionCreate,
    mentor: User = Depends(require_role(Role.mentor)),
) -> Course:
    course = store.courses.get(course_id)
    if not course or course.mentor_id != mentor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    module = next((m for m in course.modules if m.id == module_id), None)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    assignment = next((a for a in module.assignments if a.id == assignment_id), None)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    assignment.questions.append(
        MCQQuestion(
            id=store.next_id("question"),
            prompt=payload.prompt,
            options=payload.options,
        )
    )
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/submit", response_model=Course)
def submit_course(course_id: int, mentor: User = Depends(require_role(Role.mentor))) -> Course:
    course = store.courses.get(course_id)
    if not course or course.mentor_id != mentor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.status = CourseStatus.pending
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/approve", response_model=Course)
def approve_course(course_id: int, admin: User = Depends(require_role(Role.admin))) -> Course:
    _ = admin
    course = store.courses.get(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.status = CourseStatus.approved
    course.updated_at = datetime.utcnow()
    return course


@app.post("/courses/{course_id}/reject", response_model=Course)
def reject_course(course_id: int, admin: User = Depends(require_role(Role.admin))) -> Course:
    _ = admin
    course = store.courses.get(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.status = CourseStatus.rejected
    course.updated_at = datetime.utcnow()
    return course


@app.post("/enrollments", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
def enroll(payload: EnrollmentCreate, mentee: User = Depends(require_role(Role.mentee))) -> Enrollment:
    course = store.courses.get(payload.course_id)
    if not course or course.status != CourseStatus.approved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = next(
        (e for e in store.enrollments.values() if e.course_id == payload.course_id and e.mentee_id == mentee.id),
        None,
    )
    if existing:
        return existing

    enrollment = Enrollment(id=store.next_id("enrollment"), course_id=payload.course_id, mentee_id=mentee.id)
    store.enrollments[enrollment.id] = enrollment
    store.progress[enrollment.id] = Progress(enrollment_id=enrollment.id)
    return enrollment


@app.post("/enrollments/{enrollment_id}/lectures/{lecture_id}/complete")
def complete_lecture(
    enrollment_id: int,
    lecture_id: int,
    mentee: User = Depends(require_role(Role.mentee)),
) -> Dict[str, float | int]:
    enrollment = store.enrollments.get(enrollment_id)
    if not enrollment or enrollment.mentee_id != mentee.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    course = store.courses.get(enrollment.course_id)
    assert course is not None
    lecture_ids = [lecture.id for module in course.modules for lecture in module.lectures]
    if lecture_id not in lecture_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture not found")

    progress = store.progress[enrollment_id]
    if lecture_id not in progress.completed_lecture_ids:
        progress.completed_lecture_ids.append(lecture_id)

    total = len(lecture_ids) if lecture_ids else 1
    completion = (len(progress.completed_lecture_ids) / total) * 100
    return {"enrollment_id": enrollment_id, "completion_percentage": round(completion, 2)}


@app.get("/enrollments/{enrollment_id}/progress")
def get_progress(enrollment_id: int, mentee: User = Depends(require_role(Role.mentee))) -> Dict[str, float | int | List[int]]:
    enrollment = store.enrollments.get(enrollment_id)
    if not enrollment or enrollment.mentee_id != mentee.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    course = store.courses.get(enrollment.course_id)
    assert course is not None
    total_lectures = sum(len(m.lectures) for m in course.modules)
    progress = store.progress[enrollment_id]
    completion = (len(progress.completed_lecture_ids) / (total_lectures or 1)) * 100

    return {
        "enrollment_id": enrollment_id,
        "course_id": course.id,
        "completed_lecture_ids": progress.completed_lecture_ids,
        "completion_percentage": round(completion, 2),
    }
