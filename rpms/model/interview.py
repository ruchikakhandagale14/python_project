from dataclasses import dataclass
from datetime import date, time

@dataclass
class Interview:
    interview_id: int | None = None
    application_id: int = 0
    round_number: int = 1
    round_type: str = ""
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    mode: str = "ONLINE"
    interviewer_name: str = ""
    meeting_or_location: str = ""
    status: str = "SCHEDULED"


@dataclass
class InterviewFeedback:
    feedback_id: int | None = None
    interview_id: int = 0
    technical_rating: float | None = None
    communication_rating: float | None = None
    problem_solving_rating: float | None = None
    overall_rating: float | None = None
    recommendation: str = "ON_HOLD"
    remarks: str = ""
    submitted_by: int = 0
