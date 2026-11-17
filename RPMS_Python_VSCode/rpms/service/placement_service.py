from datetime import date

from rpms.exception.exceptions import InvalidStatusError, PlacementNotFoundError

OPEN_JOINING_STATUSES = ("PENDING", "DEFERRED")

class PlacementService:

    def __init__(self, placement_dao, offer_dao):
        self.placement_dao = placement_dao
        self.offer_dao = offer_dao

    def get_placement(self, placement_id):
        placement = self.placement_dao.find_by_id(placement_id)
        if not placement:
            raise PlacementNotFoundError(f"Placement ID {placement_id} not found")
        return placement

    def get_all_placements(self):
        return self.placement_dao.find_all()

    def get_placements_for_candidate(self, candidate_id):
        return self.placement_dao.find_by_candidate(candidate_id)

    def record_joining(self, placement_id, joining_date=None):
        placement = self._get_open_placement(placement_id)
        joining_date = joining_date or date.today()
        offer = self.offer_dao.find_by_id(placement.offer_id)
        self.placement_dao.mark_joined(placement, joining_date, offer.application_id)

    def defer_joining(self, placement_id, new_expected_date):
        self._get_open_placement(placement_id)
        if new_expected_date < date.today():
            raise ValueError("New joining date cannot be in the past")
        self.placement_dao.mark_deferred(placement_id, new_expected_date)

    def mark_not_joined(self, placement_id, status="NOT_JOINED"):
        status = status.upper()
        if status not in ("NOT_JOINED", "NO_SHOW"):
            raise ValueError("Status must be NOT_JOINED or NO_SHOW")
        placement = self._get_open_placement(placement_id)
        self.placement_dao.cancel(placement, status)

    def _get_open_placement(self, placement_id):
        placement = self.get_placement(placement_id)
        if placement.placement_status != "ACTIVE" or \
                placement.joining_status not in OPEN_JOINING_STATUSES:
            raise InvalidStatusError(
                f"Placement is {placement.placement_status}/"
                f"{placement.joining_status}; no further joining updates allowed"
            )
        return placement
