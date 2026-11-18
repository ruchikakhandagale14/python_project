class CandidateNotFoundError(Exception):
    pass

class JobNotFoundError(Exception):
    pass

class DuplicateApplicationError(Exception):
    pass

class CandidateNotEligibleError(Exception):
    pass

class CompanyNotFoundError(Exception):
    pass

class DuplicateCompanyError(Exception):
    pass

class ApplicationNotFoundError(Exception):
    pass

class InterviewNotFoundError(Exception):
    pass

class OfferNotFoundError(Exception):
    pass

class DuplicateOfferError(Exception):
    pass

class PlacementNotFoundError(Exception):
    pass

class InvalidStatusError(Exception):
    """Raised when an action is not allowed in the record's current status."""
    pass
