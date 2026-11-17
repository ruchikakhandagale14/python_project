import uuid
from datetime import date

from rpms.exception.exceptions import (
    ApplicationNotFoundError,
    DuplicateOfferError,
    InvalidStatusError,
    JobNotFoundError,
    OfferNotFoundError
)
from rpms.model.offer import Offer
from rpms.model.placement import Placement

# Offer closed without joining -> what happens to the application status.
CLOSE_TO_APPLICATION_STATUS = {
    "REJECTED": "WITHDRAWN",   # candidate rejected the offer
    "EXPIRED": "WITHDRAWN",    # candidate never responded
    "WITHDRAWN": "REJECTED",   # company withdrew the offer
}

class OfferService:

    def __init__(self, application_dao, job_dao, offer_dao, placement_dao):
        self.application_dao = application_dao
        self.job_dao = job_dao
        self.offer_dao = offer_dao
        self.placement_dao = placement_dao

    def create_offer(self, application_id, designation, package_lpa,
                     expected_joining_date=None, remarks=""):
        application = self.application_dao.find_by_id(application_id)
        if not application:
            raise ApplicationNotFoundError(f"Application ID {application_id} not found")

        if application.application_status != "SELECTED":
            raise InvalidStatusError(
                "Offer can be created only for SELECTED applications "
                f"(current: {application.application_status})"
            )

        if self.offer_dao.find_by_application(application_id):
            raise DuplicateOfferError("An offer already exists for this application")

        if not designation.strip():
            raise ValueError("Designation is required")

        if package_lpa < 0:
            raise ValueError("Package cannot be negative")

        if expected_joining_date and expected_joining_date < date.today():
            raise ValueError("Expected joining date cannot be in the past")

        offer = Offer(
            offer_code="OFR-" + uuid.uuid4().hex[:8].upper(),
            application_id=application_id,
            designation=designation.strip(),
            offered_package_lpa=package_lpa,
            offer_date=date.today(),
            expected_joining_date=expected_joining_date,
            remarks=remarks
        )
        return self.offer_dao.save(offer)

    def get_offer(self, offer_id):
        offer = self.offer_dao.find_by_id(offer_id)
        if not offer:
            raise OfferNotFoundError(f"Offer ID {offer_id} not found")
        return offer

    def get_all_offers(self):
        return self.offer_dao.find_all()

    def accept_offer(self, offer_id) -> int:
        """Accept an offer: creates the placement and marks the candidate PLACED."""
        offer = self._get_open_offer(offer_id)

        application = self.application_dao.find_by_id(offer.application_id)
        job = self.job_dao.find_by_id(application.job_id)
        if not job:
            raise JobNotFoundError(f"Job ID {application.job_id} not found")

        placement = Placement(
            candidate_id=application.candidate_id,
            company_id=job.company_id,
            job_id=job.job_id,
            offer_id=offer.offer_id,
            designation=offer.designation,
            final_package_lpa=offer.offered_package_lpa,
            expected_joining_date=offer.expected_joining_date
        )
        return self.placement_dao.create_from_accepted_offer(placement)

    def close_offer(self, offer_id, new_status):
        """Mark an offer REJECTED (by candidate), EXPIRED or WITHDRAWN (by company)."""
        new_status = new_status.upper()
        if new_status not in CLOSE_TO_APPLICATION_STATUS:
            raise ValueError("Status must be REJECTED, EXPIRED or WITHDRAWN")

        offer = self._get_open_offer(offer_id)
        self.offer_dao.close_offer(
            offer.offer_id,
            new_status,
            offer.application_id,
            CLOSE_TO_APPLICATION_STATUS[new_status]
        )

    def _get_open_offer(self, offer_id):
        offer = self.get_offer(offer_id)
        if offer.offer_status != "OFFERED":
            raise InvalidStatusError(
                f"Offer is already {offer.offer_status}; only OFFERED offers can change"
            )
        return offer
