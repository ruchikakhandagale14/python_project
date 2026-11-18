from rpms.dao.application_dao import set_application_status
from rpms.model.placement import Placement
from rpms.util.db_connection import get_connection, transaction

class PlacementDAO:

    def create_from_accepted_offer(self, placement: Placement) -> int:
        """Accept the offer, create the placement and mark the candidate PLACED.

        All three changes happen in one transaction.
        """
        sql = '''
            INSERT INTO placements
            (candidate_id, company_id, job_id, offer_id, designation,
             final_package_lpa, expected_joining_date, joining_status, placement_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'PENDING','ACTIVE')
        '''
        with transaction() as con:
            cur = con.cursor()
            cur.execute(sql, (
                placement.candidate_id,
                placement.company_id,
                placement.job_id,
                placement.offer_id,
                placement.designation,
                placement.final_package_lpa,
                placement.expected_joining_date
            ))
            placement_id = cur.lastrowid
            cur.execute(
                "UPDATE offers SET offer_status='ACCEPTED' WHERE offer_id=%s",
                (placement.offer_id,)
            )
            cur.execute(
                "UPDATE candidates SET placement_status='PLACED' WHERE candidate_id=%s",
                (placement.candidate_id,)
            )
            return placement_id

    def find_by_id(self, placement_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM placements WHERE placement_id=%s", (placement_id,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_all(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT * FROM placements ORDER BY placement_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def find_by_candidate(self, candidate_id: int):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM placements WHERE candidate_id=%s ORDER BY placement_id",
                (candidate_id,)
            )
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def mark_joined(self, placement: Placement, joining_date, application_id: int) -> None:
        with transaction() as con:
            cur = con.cursor()
            cur.execute(
                '''
                UPDATE placements
                SET joining_status='JOINED', actual_joining_date=%s
                WHERE placement_id=%s
                ''',
                (joining_date, placement.placement_id)
            )
            set_application_status(cur, application_id, "JOINED")

    def mark_deferred(self, placement_id: int, new_expected_date) -> None:
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(
                '''
                UPDATE placements
                SET joining_status='DEFERRED', expected_joining_date=%s
                WHERE placement_id=%s
                ''',
                (new_expected_date, placement_id)
            )
            con.commit()
        finally:
            con.close()

    def cancel(self, placement: Placement, joining_status: str) -> None:
        """Candidate did not join: cancel the placement and free the candidate."""
        with transaction() as con:
            cur = con.cursor()
            cur.execute(
                '''
                UPDATE placements
                SET joining_status=%s, placement_status='CANCELLED'
                WHERE placement_id=%s
                ''',
                (joining_status, placement.placement_id)
            )
            # Candidate goes back to NOT_PLACED only if no other active placement exists.
            cur.execute(
                '''
                UPDATE candidates
                SET placement_status='NOT_PLACED'
                WHERE candidate_id=%s
                  AND NOT EXISTS (
                      SELECT 1 FROM placements
                      WHERE candidate_id=%s
                        AND placement_status='ACTIVE'
                        AND placement_id<>%s
                  )
                ''',
                (placement.candidate_id, placement.candidate_id, placement.placement_id)
            )

    @staticmethod
    def _map(row):
        return Placement(
            placement_id=row["placement_id"],
            candidate_id=row["candidate_id"],
            company_id=row["company_id"],
            job_id=row["job_id"],
            offer_id=row["offer_id"],
            designation=row["designation"],
            final_package_lpa=float(row["final_package_lpa"] or 0),
            expected_joining_date=row["expected_joining_date"],
            actual_joining_date=row["actual_joining_date"],
            joining_status=row["joining_status"],
            placement_status=row["placement_status"]
        )
