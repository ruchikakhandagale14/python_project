from rpms.util.db_connection import get_connection

class ReportService:
    """Read-only reports. Each report returns (column_headers, rows)."""

    def _run(self, sql, headers):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql)
            return headers, cur.fetchall()
        finally:
            con.close()

    def candidate_count_by_technology(self):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                '''
                SELECT primary_technology, COUNT(*) AS total
                FROM candidates
                GROUP BY primary_technology
                ORDER BY total DESC
                '''
            )
            return cur.fetchall()
        finally:
            con.close()

    def placement_summary(self):
        return self._run(
            '''
            SELECT COUNT(*) AS total_candidates,
                   SUM(placement_status='PLACED') AS placed,
                   SUM(placement_status='NOT_PLACED') AS not_placed,
                   ROUND(100 * SUM(placement_status='PLACED') / COUNT(*), 2) AS placement_percentage
            FROM candidates
            ''',
            ["Total Candidates", "Placed", "Not Placed", "Placement %"]
        )

    def company_wise_placements(self):
        return self._run(
            '''
            SELECT c.company_name,
                   COUNT(p.placement_id) AS placements,
                   ROUND(AVG(p.final_package_lpa), 2) AS avg_package_lpa,
                   MAX(p.final_package_lpa) AS max_package_lpa
            FROM companies c
            LEFT JOIN placements p
                   ON p.company_id = c.company_id AND p.placement_status = 'ACTIVE'
            GROUP BY c.company_id, c.company_name
            ORDER BY placements DESC, c.company_name
            ''',
            ["Company", "Placements", "Avg Package (LPA)", "Max Package (LPA)"]
        )

    def applications_by_status(self):
        return self._run(
            '''
            SELECT application_status, COUNT(*) AS total
            FROM applications
            GROUP BY application_status
            ORDER BY total DESC
            ''',
            ["Application Status", "Total"]
        )

    def job_wise_applications(self):
        return self._run(
            '''
            SELECT j.job_code, j.job_title, c.company_name,
                   j.openings, COUNT(a.application_id) AS applications
            FROM jobs j
            JOIN companies c ON c.company_id = j.company_id
            LEFT JOIN applications a ON a.job_id = j.job_id
            GROUP BY j.job_id, j.job_code, j.job_title, c.company_name, j.openings
            ORDER BY applications DESC, j.job_code
            ''',
            ["Job Code", "Job Title", "Company", "Openings", "Applications"]
        )

    def upcoming_interviews(self):
        return self._run(
            '''
            SELECT i.interview_id, ca.full_name, j.job_title,
                   i.round_number, i.round_type, i.scheduled_date,
                   i.scheduled_time, i.mode, i.status
            FROM interview_rounds i
            JOIN applications a ON a.application_id = i.application_id
            JOIN candidates ca ON ca.candidate_id = a.candidate_id
            JOIN jobs j ON j.job_id = a.job_id
            WHERE i.status IN ('SCHEDULED','RESCHEDULED')
              AND i.scheduled_date >= CURDATE()
            ORDER BY i.scheduled_date, i.scheduled_time
            ''',
            ["Interview ID", "Candidate", "Job", "Round", "Type",
             "Date", "Time", "Mode", "Status"]
        )

    def offers_by_status(self):
        return self._run(
            '''
            SELECT offer_status, COUNT(*) AS total,
                   ROUND(AVG(offered_package_lpa), 2) AS avg_package_lpa
            FROM offers
            GROUP BY offer_status
            ORDER BY total DESC
            ''',
            ["Offer Status", "Total", "Avg Package (LPA)"]
        )

    def highest_package_placements(self, limit: int = 5):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                '''
                SELECT ca.full_name, c.company_name, p.designation,
                       p.final_package_lpa, p.joining_status
                FROM placements p
                JOIN candidates ca ON ca.candidate_id = p.candidate_id
                JOIN companies c ON c.company_id = p.company_id
                WHERE p.placement_status = 'ACTIVE'
                ORDER BY p.final_package_lpa DESC
                LIMIT %s
                ''',
                (int(limit),)
            )
            headers = ["Candidate", "Company", "Designation",
                       "Package (LPA)", "Joining Status"]
            return headers, cur.fetchall()
        finally:
            con.close()

    def technology_wise_placements(self):
        return self._run(
            '''
            SELECT COALESCE(ca.primary_technology,'Unknown') AS technology,
                   COUNT(*) AS candidates,
                   SUM(ca.placement_status='PLACED') AS placed
            FROM candidates ca
            GROUP BY COALESCE(ca.primary_technology,'Unknown')
            ORDER BY placed DESC, candidates DESC
            ''',
            ["Technology", "Candidates", "Placed"]
        )
