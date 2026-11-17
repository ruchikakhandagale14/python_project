from rpms.model.company import Company
from rpms.util.db_connection import get_connection

class CompanyDAO:

    def save(self, company: Company) -> int:
        sql = '''
            INSERT INTO companies
            (company_code, company_name, industry, location, hr_name, hr_email, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        '''
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (
                company.company_code,
                company.company_name,
                company.industry,
                company.location,
                company.hr_name,
                company.hr_email,
                company.status
            ))
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def find_by_id(self, company_id: int):
        return self._find_one("SELECT * FROM companies WHERE company_id=%s", company_id)

    def find_by_code(self, company_code: str):
        return self._find_one("SELECT * FROM companies WHERE company_code=%s", company_code)

    def _find_one(self, sql: str, value):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(sql, (value,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_all(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM companies ORDER BY company_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def update(self, company: Company) -> None:
        sql = '''
            UPDATE companies
            SET company_name=%s, industry=%s, location=%s, hr_name=%s, hr_email=%s
            WHERE company_id=%s
        '''
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, (
                company.company_name,
                company.industry,
                company.location,
                company.hr_name,
                company.hr_email,
                company.company_id
            ))
            con.commit()
        finally:
            con.close()

    def update_status(self, company_id: int, status: str) -> None:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                "UPDATE companies SET status=%s WHERE company_id=%s",
                (status, company_id)
            )
            con.commit()
        finally:
            con.close()

    @staticmethod
    def _map(row):
        return Company(
            company_id=row["company_id"],
            company_code=row["company_code"],
            company_name=row["company_name"],
            industry=row["industry"] or "",
            location=row["location"] or "",
            hr_name=row["hr_name"] or "",
            hr_email=row["hr_email"] or "",
            status=row["status"]
        )
