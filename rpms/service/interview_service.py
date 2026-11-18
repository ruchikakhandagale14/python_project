from datetime import date, time

from rpms.exception.exceptions import (
    ApplicationNotFoundError,
    InterviewNotFoundError,
    InvalidStatusError
)
from rpms.model.interview import Interview, InterviewFeedback

WORK_START = time(9, 0)
WORK_END = time(18, 0)
VALID_MODES = ("ONLINE", "OFFLINE", "TELEPHONIC")
VALID_RECOMMENDATIONS = ("NEXT_ROUND", "SELECTED", "REJECTED", "ON_HOLD")
FINAL_STATUSES = ("REJECTED", "WITHDRAWN", "OFFERED", "JOINED")

# What the application status becomes after interview feedback.
RECOMMENDATION_TO_APPLICATION_STATUS = {
    "NEXT_ROUND": "INTERVIEWED",
    "ON_HOLD": "INTERVIEWED",
    "SELECTED": "SELECTED",
    "REJECTED": "REJECTED",
}

class InterviewService:

    def __init__(self, application_dao, interview_dao):
        self.application_dao = application_dao
        self.interview_dao = interview_dao

    def schedule_interview(self, application_id, round_type, scheduled_date,
                           scheduled_time, mode, interviewer_name="",
                           meeting_or_location=""):
        application = self.application_dao.find_by_id(application_id)
        if not application:
            raise ApplicationNotFoundError(f"Application ID {application_id} not found")

        if application.eligibility_status != "ELIGIBLE":
            raise InvalidStatusError("Application is not ELIGIBLE for interviews")

        if application.application_status in FINAL_STATUSES:
            raise InvalidStatusError(
                f"Cannot schedule interview: application is {application.application_status}"
            )

        mode = mode.upper()
        if mode not in VALID_MODES:
            raise ValueError("Mode must be ONLINE, OFFLINE or TELEPHONIC")

        if not round_type.strip():
            raise ValueError("Round type is required (e.g. Technical, HR)")

        if scheduled_date < date.today():
            raise ValueError("Interview date cannot be in the past")

        if not (WORK_START <= scheduled_time <= WORK_END):
            raise ValueError("Interview time must be between 09:00 and 18:00")

        # A new round can start only after the previous round is finished.
        for existing in self.interview_dao.find_by_application(application_id):
            if existing.status in ("SCHEDULED", "RESCHEDULED"):
                raise InvalidStatusError(
                    f"Round {existing.round_number} is still {existing.status}; "
                    "complete or cancel it first"
                )

        interview = Interview(
            application_id=application_id,
            round_number=self.interview_dao.next_round_number(application_id),
            round_type=round_type.strip(),
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            mode=mode,
            interviewer_name=interviewer_name,
            meeting_or_location=meeting_or_location
        )
        return self.interview_dao.save(interview)

    def get_interview(self, interview_id):
        interview = self.interview_dao.find_by_id(interview_id)
        if not interview:
            raise InterviewNotFoundError(f"Interview ID {interview_id} not found")
        return interview

    def get_interviews_for_application(self, application_id):
        return self.interview_dao.find_by_application(application_id)

    def get_upcoming_interviews(self):
        return self.interview_dao.find_upcoming()

    def reschedule(self, interview_id, new_date, new_time):
        interview = self.get_interview(interview_id)
        if interview.status not in ("SCHEDULED", "RESCHEDULED"):
            raise InvalidStatusError(f"Cannot reschedule a {interview.status} interview")
        if new_date < date.today():
            raise ValueError("New date cannot be in the past")
        self.interview_dao.reschedule(interview_id, new_date, new_time)

    def cancel(self, interview_id):
        self._close(interview_id, "CANCELLED")

    def mark_no_show(self, interview_id):
        self._close(interview_id, "NO_SHOW")

    def _close(self, interview_id, new_status):
        interview = self.get_interview(interview_id)
        if interview.status not in ("SCHEDULED", "RESCHEDULED"):
            raise InvalidStatusError(
                f"Cannot change a {interview.status} interview to {new_status}"
            )
        self.interview_dao.update_status(interview_id, new_status)

    def submit_feedback(self, interview_id, submitted_by, recommendation,
                        technical_rating=None, communication_rating=None,
                        problem_solving_rating=None, overall_rating=None,
                        remarks=""):
        interview = self.get_interview(interview_id)

        if interview.status not in ("SCHEDULED", "RESCHEDULED"):
            raise InvalidStatusError(
                f"Feedback not allowed: interview is {interview.status}"
            )

        if self.interview_dao.feedback_exists(interview_id):
            raise InvalidStatusError("Feedback already submitted for this interview")

        recommendation = recommendation.upper()
        if recommendation not in VALID_RECOMMENDATIONS:
            raise ValueError(
                "Recommendation must be one of: " + ", ".join(VALID_RECOMMENDATIONS)
            )

        for name, rating in (
            ("Technical", technical_rating),
            ("Communication", communication_rating),
            ("Problem solving", problem_solving_rating),
            ("Overall", overall_rating),
        ):
            if rating is not None and not (0 <= rating <= 5):
                raise ValueError(f"{name} rating must be between 0 and 5")

        feedback = InterviewFeedback(
            interview_id=interview_id,
            technical_rating=technical_rating,
            communication_rating=communication_rating,
            problem_solving_rating=problem_solving_rating,
            overall_rating=overall_rating,
            recommendation=recommendation,
            remarks=remarks,
            submitted_by=submitted_by
        )

        return self.interview_dao.save_feedback(
            feedback,
            interview.application_id,
            RECOMMENDATION_TO_APPLICATION_STATUS[recommendation]
        )
