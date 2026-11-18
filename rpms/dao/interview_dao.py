from rpms.dao.application_dao import set_application_status
from rpms.model.interview import Interview, InterviewFeedback
from rpms.util.db_connection import get_connection, transaction

class InterviewDAO:

    def save(self, interview: Interview) -> int:
        """Insert the round and mark the application INTERVIEW_SCHEDULED."""
        sql = '''
            INSERT INTO interview_rounds
            (application_id, round_number, round_type, scheduled_date,
             scheduled_time, mode, interviewer_name, meeting_or_location, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        with transaction() as con:
            cur = con.cursor()
            cur.execute(sql, (
                interview.application_id,
                interview.round_number,
                interview.round_type,
                interview.scheduled_date,
                interview.scheduled_time,
                interview.mode,
                interview.interviewer_name or None,
                interview.meeting_or_location or None,
                interview.status
            ))
            interview_id = cur.lastrowid
            set_application_status(cur, interview.application_id, "INTERVIEW_SCHEDULED")
            return interview_id

    def next_round_number(self, application_id: int) -> int:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT COALESCE(MAX(round_number),0)+1 FROM interview_rounds WHERE application_id=%s",
                (application_id,)
            )
            return int(cur.fetchone()[0])
        finally:
            con.close()

    def find_by_id(self, interview_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM interview_rounds WHERE interview_id=%s", (interview_id,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_by_application(self, application_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM interview_rounds WHERE application_id=%s ORDER BY round_number",
                (application_id,)
            )
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def find_upcoming(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                '''
                SELECT * FROM interview_rounds
                WHERE status IN ('SCHEDULED','RESCHEDULED')
                  AND scheduled_date >= CURDATE()
                ORDER BY scheduled_date, scheduled_time
                '''
            )
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def update_status(self, interview_id: int, status: str) -> None:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE interview_rounds SET status=%s WHERE interview_id=%s",
                (status, interview_id)
            )
            con.commit()
        finally:
            con.close()

    def reschedule(self, interview_id: int, new_date, new_time) -> None:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                '''
                UPDATE interview_rounds
                SET scheduled_date=%s, scheduled_time=%s, status='RESCHEDULED'
                WHERE interview_id=%s
                ''',
                (new_date, new_time, interview_id)
            )
            con.commit()
        finally:
            con.close()

    def save_feedback(self, fb: InterviewFeedback, application_id: int,
                      new_application_status: str) -> int:
        """Store feedback, complete the round and update the application together."""
        sql = '''
            INSERT INTO interview_feedback
            (interview_id, technical_rating, communication_rating,
             problem_solving_rating, overall_rating, recommendation,
             remarks, submitted_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        with transaction() as con:
            cur = con.cursor()
            cur.execute(sql, (
                fb.interview_id,
                fb.technical_rating,
                fb.communication_rating,
                fb.problem_solving_rating,
                fb.overall_rating,
                fb.recommendation,
                fb.remarks or None,
                fb.submitted_by
            ))
            feedback_id = cur.lastrowid
            cur.execute(
                "UPDATE interview_rounds SET status='COMPLETED' WHERE interview_id=%s",
                (fb.interview_id,)
            )
            set_application_status(cur, application_id, new_application_status)
            return feedback_id

    def feedback_exists(self, interview_id: int) -> bool:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT 1 FROM interview_feedback WHERE interview_id=%s",
                (interview_id,)
            )
            return cur.fetchone() is not None
        finally:
            con.close()

    @staticmethod
    def _map(row):
        return Interview(
            interview_id=row["interview_id"],
            application_id=row["application_id"],
            round_number=row["round_number"],
            round_type=row["round_type"],
            scheduled_date=row["scheduled_date"],
            scheduled_time=row["scheduled_time"],
            mode=row["mode"],
            interviewer_name=row["interviewer_name"] or "",
            meeting_or_location=row["meeting_or_location"] or "",
            status=row["status"]
        )
