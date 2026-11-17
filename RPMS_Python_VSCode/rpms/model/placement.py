from dataclasses import dataclass
from datetime import date

@dataclass
class Placement:
    placement_id: int | None = None
    candidate_id: int = 0
    company_id: int = 0
    job_id: int = 0
    offer_id: int = 0
    designation: str = ""
    final_package_lpa: float = 0.0
    expected_joining_date: date | None = None
    actual_joining_date: date | None = None
    joining_status: str = "PENDING"
    placement_status: str = "ACTIVE"
