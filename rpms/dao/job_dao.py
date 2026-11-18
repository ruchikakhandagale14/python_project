from datetime import date

from rpms.model.job import Job
from rpms.util.db_connection import get_connection

class JobDAO:

    def save(self, job: Job, created_by: int) -> int:
        sql = '''
            INSERT INTO jobs
            (job_code, company_id, job_title, location, openings,
             min_package_lpa, max_package_lpa, min_percentage,
             min_passing_year, max_passing_year, max_backlogs,
             posted_date, application_deadline, status, created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (
                job.job_code,
                job.company_id,
                job.job_title,
                job.location,
                job.openings,
                job.min_package_lpa,
                job.max_package_lpa,
                job.min_percentage,
                job.min_passing_year or None,
                job.max_passing_year or None,
                job.max_backlogs,
                date.today(),
                job.application_deadline,
                job.status,
                created_by
            ))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def find_by_id(self, job_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM jobs WHERE job_id=%s", (job_id,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_by_code(self, job_code: str):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM jobs WHERE job_code=%s", (job_code,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_open_jobs(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM jobs WHERE status='OPEN' ORDER BY job_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def find_all(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM jobs ORDER BY job_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def find_by_company(self, company_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM jobs WHERE company_id=%s ORDER BY job_id",
                (company_id,)
            )
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def update_status(self, job_id: int, status: str) -> None:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("UPDATE jobs SET status=%s WHERE job_id=%s", (status, job_id))
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _map(row):
        return Job(
            job_id=row["job_id"],
            job_code=row["job_code"],
            company_id=row["company_id"],
            job_title=row["job_title"],
            location=row["location"],
            openings=row["openings"],
            min_package_lpa=float(row["min_package_lpa"] or 0),
            max_package_lpa=float(row["max_package_lpa"] or 0),
            min_percentage=float(row["min_percentage"] or 0),
            min_passing_year=row["min_passing_year"] or 0,
            max_passing_year=row["max_passing_year"] or 0,
            max_backlogs=row["max_backlogs"],
            application_deadline=row["application_deadline"],
            status=row["status"]
        )
