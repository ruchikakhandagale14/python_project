from datetime import date

from rpms.exception.exceptions import (
    CompanyNotFoundError,
    InvalidStatusError,
    JobNotFoundError
)
from rpms.util.validation import is_valid_percentage

class JobService:

    def __init__(self, job_dao, company_dao):
        self.job_dao = job_dao
        self.company_dao = company_dao

    def add_job(self, job, created_by: int):
        company = self.company_dao.find_by_id(job.company_id)
        if not company:
            raise CompanyNotFoundError(f"Company ID {job.company_id} not found")

        if company.status.upper() != "ACTIVE":
            raise InvalidStatusError("Cannot post a job for an INACTIVE company")

        if not job.job_code.strip() or not job.job_title.strip():
            raise ValueError("Job code and job title are required")

        if self.job_dao.find_by_code(job.job_code):
            raise ValueError(f"Job code {job.job_code} already exists")

        if job.openings <= 0:
            raise ValueError("Openings must be greater than 0")

        if job.min_package_lpa > job.max_package_lpa:
            raise ValueError("Minimum package cannot be greater than maximum package")

        if not is_valid_percentage(job.min_percentage):
            raise ValueError("Minimum percentage must be 0-100")

        if job.max_backlogs < 0:
            raise ValueError("Max backlogs cannot be negative")

        if job.application_deadline is None or job.application_deadline < date.today():
            raise ValueError("Application deadline must be today or a future date")

        return self.job_dao.save(job, created_by)

    def get_job(self, job_id):
        job = self.job_dao.find_by_id(job_id)
        if not job:
            raise JobNotFoundError(f"Job ID {job_id} not found")
        return job

    def get_all_jobs(self):
        return self.job_dao.find_all()

    def get_open_jobs(self):
        return self.job_dao.find_open_jobs()

    def get_jobs_by_company(self, company_id):
        return self.job_dao.find_by_company(company_id)

    def close_job(self, job_id):
        job = self.get_job(job_id)
        if job.status.upper() != "OPEN":
            raise InvalidStatusError(f"Only OPEN jobs can be closed (current: {job.status})")
        self.job_dao.update_status(job_id, "CLOSED")
