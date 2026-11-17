from rpms.model.application import Application
from rpms.util.db_connection import get_connection

def set_application_status(cur, application_id: int, status: str) -> None:
    """Update an application's status using an already-open cursor.

    Lets other DAOs change the application status inside their own
    transaction, so both tables are updated together or not at all.
    """
    cur.execute(
        "UPDATE applications SET application_status=%s WHERE application_id=%s",
        (status, application_id)
    )


class ApplicationDAO:

    def save(self, app: Application) -> int:
        sql = '''
            INSERT INTO applications
            (application_code,candidate_id,job_id,eligibility_status,
             eligibility_reason,application_status)
            VALUES (%s,%s,%s,%s,%s,%s)
        '''
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (
                app.application_code,
                app.candidate_id,
                app.job_id,
                app.eligibility_status,
                app.eligibility_reason,
                app.application_status
            ))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def exists(self, candidate_id: int, job_id: int) -> bool:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT 1 FROM applications WHERE candidate_id=%s AND job_id=%s",
                (candidate_id, job_id)
            )
            return cur.fetchone() is not None
        finally:
            con.close()

    def find_by_id(self, application_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM applications WHERE application_id=%s",
                (application_id,)
            )
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_by_candidate(self, candidate_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM applications WHERE candidate_id=%s ORDER BY application_id DESC",
                (candidate_id,)
            )
            return cur.fetchall()
        finally:
            con.close()

    def find_all(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM applications ORDER BY application_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def update_status(self, application_id: int, status: str) -> None:
        con = get_connection()
        try:
            cur = con.cursor()
            set_application_status(cur, application_id, status)
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _map(row):
        return Application(
            application_id=row["application_id"],
            application_code=row["application_code"],
            candidate_id=row["candidate_id"],
            job_id=row["job_id"],
            applied_at=row["applied_at"],
            eligibility_status=row["eligibility_status"],
            eligibility_reason=row["eligibility_reason"] or "",
            application_status=row["application_status"]
        )
