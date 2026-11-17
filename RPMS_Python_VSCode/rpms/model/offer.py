from dataclasses import dataclass
from datetime import date

@dataclass
class Offer:
    offer_id: int | None = None
    offer_code: str = ""
    application_id: int = 0
    designation: str = ""
    offered_package_lpa: float = 0.0
    offer_date: date | None = None
    expected_joining_date: date | None = None
    offer_status: str = "OFFERED"
    remarks: str = ""
