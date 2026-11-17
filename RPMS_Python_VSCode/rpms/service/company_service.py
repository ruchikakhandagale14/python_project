from rpms.exception.exceptions import (
    CompanyNotFoundError,
    DuplicateCompanyError,
    InvalidStatusError
)
from rpms.util.validation import is_valid_email

VALID_STATUSES = ("ACTIVE", "INACTIVE")

class CompanyService:

    def __init__(self, company_dao):
        self.company_dao = company_dao

    def add_company(self, company):
        if not company.company_code.strip():
            raise ValueError("Company code is required")

        if not company.company_name.strip():
            raise ValueError("Company name is required")

        if company.hr_email and not is_valid_email(company.hr_email):
            raise ValueError("Invalid HR email")

        if self.company_dao.find_by_code(company.company_code):
            raise DuplicateCompanyError(
                f"Company code {company.company_code} already exists"
            )

        return self.company_dao.save(company)

    def get_company(self, company_id):
        company = self.company_dao.find_by_id(company_id)
        if not company:
            raise CompanyNotFoundError(f"Company ID {company_id} not found")
        return company

    def get_all_companies(self):
        return self.company_dao.find_all()

    def update_company(self, company_id, company_name=None, industry=None,
                       location=None, hr_name=None, hr_email=None):
        """Update only the fields that are given (None or empty = keep old value)."""
        company = self.get_company(company_id)

        if hr_email and not is_valid_email(hr_email):
            raise ValueError("Invalid HR email")

        company.company_name = company_name or company.company_name
        company.industry = industry or company.industry
        company.location = location or company.location
        company.hr_name = hr_name or company.hr_name
        company.hr_email = hr_email or company.hr_email

        self.company_dao.update(company)
        return company

    def set_status(self, company_id, status):
        status = status.upper()
        if status not in VALID_STATUSES:
            raise InvalidStatusError("Status must be ACTIVE or INACTIVE")
        self.get_company(company_id)
        self.company_dao.update_status(company_id, status)
