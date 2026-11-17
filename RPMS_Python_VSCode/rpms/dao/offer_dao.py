from rpms.dao.application_dao import set_application_status
from rpms.model.offer import Offer
from rpms.util.db_connection import get_connection, transaction

class OfferDAO:

    def save(self, offer: Offer) -> int:
        """Insert the offer and mark the application OFFERED."""
        sql = '''
            INSERT INTO offers
            (offer_code, application_id, designation, offered_package_lpa,
             offer_date, expected_joining_date, offer_status, remarks)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        with transaction() as con:
            cur = con.cursor()
            cur.execute(sql, (
                offer.offer_code,
                offer.application_id,
                offer.designation,
                offer.offered_package_lpa,
                offer.offer_date,
                offer.expected_joining_date,
                offer.offer_status,
                offer.remarks or None
            ))
            offer_id = cur.lastrowid
            set_application_status(cur, offer.application_id, "OFFERED")
            return offer_id

    def find_by_id(self, offer_id: int):
        return self._find_one("SELECT * FROM offers WHERE offer_id=%s", offer_id)

    def find_by_application(self, application_id: int):
        return self._find_one("SELECT * FROM offers WHERE application_id=%s", application_id)

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
            cur.execute("SELECT * FROM offers ORDER BY offer_id")
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def close_offer(self, offer_id: int, offer_status: str,
                    application_id: int, application_status: str) -> None:
        """Reject/expire/withdraw an offer and update the application together."""
        with transaction() as con:
            cur = con.cursor()
            cur.execute(
                "UPDATE offers SET offer_status=%s WHERE offer_id=%s",
                (offer_status, offer_id)
            )
            set_application_status(cur, application_id, application_status)

    @staticmethod
    def _map(row):
        return Offer(
            offer_id=row["offer_id"],
            offer_code=row["offer_code"],
            application_id=row["application_id"],
            designation=row["designation"],
            offered_package_lpa=float(row["offered_package_lpa"] or 0),
            offer_date=row["offer_date"],
            expected_joining_date=row["expected_joining_date"],
            offer_status=row["offer_status"],
            remarks=row["remarks"] or ""
        )
