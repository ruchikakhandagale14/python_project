from datetime import datetime

from rpms.dao.application_dao import ApplicationDAO
from rpms.dao.candidate_dao import CandidateDAO
from rpms.dao.company_dao import CompanyDAO
from rpms.dao.interview_dao import InterviewDAO
from rpms.dao.job_dao import JobDAO
from rpms.dao.offer_dao import OfferDAO
from rpms.dao.placement_dao import PlacementDAO

from rpms.model.candidate import Candidate
from rpms.model.company import Company
from rpms.model.job import Job

from rpms.service.activity_log_service import ActivityLogService
from rpms.service.application_service import ApplicationService
from rpms.service.candidate_service import CandidateService
from rpms.service.company_service import CompanyService
from rpms.service.eligibility_service import EligibilityService
from rpms.service.interview_service import InterviewService
from rpms.service.job_service import JobService
from rpms.service.offer_service import OfferService
from rpms.service.placement_service import PlacementService
from rpms.service.report_service import ReportService

from rpms.util.display import print_dict, print_records, print_table


# ---------------------------------------------------------------- input helpers

def ask(prompt, default=None):
    value = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return value or (default or "")

def ask_int(prompt):
    return int(input(f"{prompt}: ").strip())

def ask_float(prompt):
    return float(input(f"{prompt}: ").strip())

def ask_date(prompt, required=True):
    text = input(f"{prompt} (YYYY-MM-DD){'' if required else ', blank to skip'}: ").strip()
    if not text and not required:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()

def ask_time(prompt):
    text = input(f"{prompt} (HH:MM, 24-hour): ").strip()
    return datetime.strptime(text, "%H:%M").time()

def ask_rating(prompt):
    text = input(f"{prompt} (0-5, blank to skip): ").strip()
    return float(text) if text else None


# ----------------------------------------------------------------------- menus

def print_menu():
    print("\n==================================")
    print("RECRUITMENT & PLACEMENT MANAGEMENT SYSTEM (RPMS)")
    print("==================================")
    print("1. Candidate Management")
    print("2. Company Management")
    print("3. Job Management")
    print("4. Apply for Job (Eligibility Check)")
    print("5. Interview Management")
    print("6. Offer Management")
    print("7. Placement Management")
    print("8. Reports")
    print("9. Exit")


def candidate_menu(ctx):
    print("\n-- Candidate Management --")
    print("1. View Candidates\n2. Add Candidate\n3. Search Candidate by ID\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        print_records(ctx.candidates.get_all_candidates())

    elif choice == 2:
        candidate = Candidate(
            candidate_code=ask("Candidate Code"),
            full_name=ask("Full Name"),
            email=ask("Email"),
            mobile=ask("Mobile"),
            qualification=ask("Qualification"),
            passing_year=ask_int("Passing Year"),
            percentage=ask_float("Percentage"),
            backlog_count=ask_int("Backlog Count"),
            primary_technology=ask("Main Skill / Technology")
        )
        candidate_id = ctx.candidates.add_candidate(candidate)
        print(f"Candidate created. ID = {candidate_id}")
        ctx.log.log(f"Candidate created: {candidate.candidate_code}")

    elif choice == 3:
        print_dict(ctx.candidates.get_candidate(ask_int("Candidate ID")))


def company_menu(ctx):
    print("\n-- Company Management --")
    print("1. View Companies\n2. Add Company\n3. Update Company\n"
          "4. Change Company Status (Active/Inactive)\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        print_records(ctx.companies.get_all_companies())

    elif choice == 2:
        company = Company(
            company_code=ask("Company Code (e.g. COM-009)"),
            company_name=ask("Company Name"),
            industry=ask("Industry"),
            location=ask("Location"),
            hr_name=ask("HR Name"),
            hr_email=ask("HR Email")
        )
        company_id = ctx.companies.add_company(company)
        print(f"Company created. ID = {company_id}")
        ctx.log.log(f"Company created: {company.company_code}")

    elif choice == 3:
        company_id = ask_int("Company ID")
        print("Leave a field blank to keep the old value.")
        ctx.companies.update_company(
            company_id,
            company_name=ask("New Company Name"),
            industry=ask("New Industry"),
            location=ask("New Location"),
            hr_name=ask("New HR Name"),
            hr_email=ask("New HR Email")
        )
        print("Company updated.")
        ctx.log.log(f"Company updated: id={company_id}")

    elif choice == 4:
        company_id = ask_int("Company ID")
        status = ask("New status (ACTIVE/INACTIVE)")
        ctx.companies.set_status(company_id, status)
        print("Company status updated.")
        ctx.log.log(f"Company status: id={company_id}, status={status.upper()}")


def job_menu(ctx):
    print("\n-- Job Management --")
    print("1. View Open Jobs\n2. View All Jobs\n3. Add Job\n4. Close Job\n"
          "5. Jobs of a Company\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        print_records(ctx.jobs.get_open_jobs())

    elif choice == 2:
        print_records(ctx.jobs.get_all_jobs())

    elif choice == 3:
        job = Job(
            job_code=ask("Job Code (e.g. JOB-2026-010)"),
            company_id=ask_int("Company ID"),
            job_title=ask("Job Title"),
            location=ask("Location"),
            openings=ask_int("Openings"),
            min_package_lpa=ask_float("Minimum Salary Package (LPA)"),
            max_package_lpa=ask_float("Maximum Package (LPA)"),
            min_percentage=ask_float("Minimum Percentage"),
            min_passing_year=ask_int("Minimum Passing Year"),
            max_passing_year=ask_int("Maximum Passing Year"),
            max_backlogs=ask_int("Max Backlogs Allowed"),
            application_deadline=ask_date("Application Deadline")
        )
        created_by = ask_int("Created by (User ID, e.g. 2)")
        job_id = ctx.jobs.add_job(job, created_by)
        print(f"Job created. ID = {job_id}")
        ctx.log.log(f"Job created: {job.job_code}")

    elif choice == 4:
        job_id = ask_int("Job ID")
        ctx.jobs.close_job(job_id)
        print("Job closed.")
        ctx.log.log(f"Job closed: id={job_id}")

    elif choice == 5:
        print_records(ctx.jobs.get_jobs_by_company(ask_int("Company ID")))


def application_menu(ctx):
    print("\n-- Job Application --")
    print("1. Apply for Job\n2. Check Eligibility (without applying)\n"
          "3. View Applications of a Candidate\n4. View All Applications\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        candidate_id = ask_int("Candidate ID")
        job_id = ask_int("Job ID")
        application_id = ctx.applications.apply_for_job(candidate_id, job_id)
        print(f"Application created. ID = {application_id}")
        ctx.log.log(f"Application created: candidate={candidate_id}, job={job_id}")

    elif choice == 2:
        candidate = ctx.candidates.get_candidate(ask_int("Candidate ID"))
        job = ctx.jobs.get_job(ask_int("Job ID"))
        reasons = ctx.eligibility.get_failure_reasons(candidate, job)
        if reasons:
            print("NOT ELIGIBLE:")
            for reason in reasons:
                print(" -", reason)
        else:
            print("ELIGIBLE: candidate meets all criteria.")

    elif choice == 3:
        print_records(ctx.application_dao.find_by_candidate(ask_int("Candidate ID")))

    elif choice == 4:
        print_records(ctx.application_dao.find_all())


def interview_menu(ctx):
    print("\n-- Interview Management --")
    print("1. Schedule Interview\n2. Reschedule Interview\n3. Cancel Interview\n"
          "4. Mark Candidate as No-Show\n5. Submit Feedback / Result\n"
          "6. Interviews of an Application\n7. Upcoming Interviews\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        application_id = ask_int("Application ID")
        interview_id = ctx.interviews.schedule_interview(
            application_id=application_id,
            round_type=ask("Round Type (Technical/HR/Managerial)"),
            scheduled_date=ask_date("Interview Date"),
            scheduled_time=ask_time("Interview Time"),
            mode=ask("Mode (ONLINE/OFFLINE/TELEPHONIC)", "ONLINE"),
            interviewer_name=ask("Interviewer Name"),
            meeting_or_location=ask("Meeting Link / Location")
        )
        print(f"Interview scheduled. ID = {interview_id}")
        ctx.log.log(f"Interview scheduled: id={interview_id}, application={application_id}")

    elif choice == 2:
        interview_id = ask_int("Interview ID")
        ctx.interviews.reschedule(interview_id, ask_date("New Date"), ask_time("New Time"))
        print("Interview rescheduled.")
        ctx.log.log(f"Interview rescheduled: id={interview_id}")

    elif choice == 3:
        interview_id = ask_int("Interview ID")
        ctx.interviews.cancel(interview_id)
        print("Interview cancelled.")
        ctx.log.log(f"Interview cancelled: id={interview_id}")

    elif choice == 4:
        interview_id = ask_int("Interview ID")
        ctx.interviews.mark_no_show(interview_id)
        print("Interview marked NO_SHOW.")
        ctx.log.log(f"Interview no-show: id={interview_id}")

    elif choice == 5:
        interview_id = ask_int("Interview ID")
        feedback_id = ctx.interviews.submit_feedback(
            interview_id=interview_id,
            submitted_by=ask_int("Your User ID (e.g. 2)"),
            recommendation=ask("Recommendation (NEXT_ROUND/SELECTED/REJECTED/ON_HOLD)"),
            technical_rating=ask_rating("Technical rating"),
            communication_rating=ask_rating("Communication rating"),
            problem_solving_rating=ask_rating("Problem solving rating"),
            overall_rating=ask_rating("Overall rating"),
            remarks=ask("Remarks")
        )
        print(f"Feedback saved. ID = {feedback_id}")
        ctx.log.log(f"Interview feedback: interview={interview_id}, feedback={feedback_id}")

    elif choice == 6:
        print_records(ctx.interviews.get_interviews_for_application(ask_int("Application ID")))

    elif choice == 7:
        print_records(ctx.interviews.get_upcoming_interviews())


def offer_menu(ctx):
    print("\n-- Offer Management --")
    print("1. Create Offer\n2. View Offers\n3. Accept Offer & Create Placement\n"
          "4. Reject / Expire / Withdraw Offer\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        application_id = ask_int("Application ID (must be SELECTED)")
        offer_id = ctx.offers.create_offer(
            application_id=application_id,
            designation=ask("Designation"),
            package_lpa=ask_float("Package (LPA)"),
            expected_joining_date=ask_date("Expected Joining Date", required=False),
            remarks=ask("Remarks")
        )
        print(f"Offer created. ID = {offer_id}")
        ctx.log.log(f"Offer created: id={offer_id}, application={application_id}")

    elif choice == 2:
        print_records(ctx.offers.get_all_offers())

    elif choice == 3:
        offer_id = ask_int("Offer ID")
        placement_id = ctx.offers.accept_offer(offer_id)
        print(f"Offer accepted. Placement created. ID = {placement_id}")
        ctx.log.log(f"Offer accepted: id={offer_id}, placement={placement_id}")

    elif choice == 4:
        offer_id = ask_int("Offer ID")
        status = ask("New status (REJECTED/EXPIRED/WITHDRAWN)")
        ctx.offers.close_offer(offer_id, status)
        print(f"Offer marked {status.upper()}.")
        ctx.log.log(f"Offer {status.upper()}: id={offer_id}")


def placement_menu(ctx):
    print("\n-- Placement Management --")
    print("1. View Placements\n2. Record Joining\n3. Defer Joining\n"
          "4. Cancel Placement (Not Joined / No-Show)\n5. Placements of a Candidate\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        print_records(ctx.placements.get_all_placements())

    elif choice == 2:
        placement_id = ask_int("Placement ID")
        joining_date = ask_date("Actual Joining Date", required=False)
        ctx.placements.record_joining(placement_id, joining_date)
        print("Joining recorded. Placement status: JOINED.")
        ctx.log.log(f"Placement joined: id={placement_id}")

    elif choice == 3:
        placement_id = ask_int("Placement ID")
        ctx.placements.defer_joining(placement_id, ask_date("New Expected Joining Date"))
        print("Joining deferred.")
        ctx.log.log(f"Placement deferred: id={placement_id}")

    elif choice == 4:
        placement_id = ask_int("Placement ID")
        status = ask("Status (NOT_JOINED/NO_SHOW)", "NOT_JOINED")
        ctx.placements.mark_not_joined(placement_id, status)
        print("Placement cancelled; candidate is available again.")
        ctx.log.log(f"Placement {status.upper()}: id={placement_id}")

    elif choice == 5:
        print_records(ctx.placements.get_placements_for_candidate(ask_int("Candidate ID")))


def report_menu(ctx):
    r = ctx.reports
    print("\n-- Reports --")
    print("1. Candidate Technology Report\n2. Placement Summary\n"
          "3. Company-wise Placements\n4. Applications by Status\n"
          "5. Job-wise Applications\n6. Upcoming Interviews\n"
          "7. Offers by Status\n8. Top Packages\n"
          "9. Technology-wise Placements\n10. Candidates Not Placed\n0. Back")
    choice = ask_int("Enter Your Choice")

    if choice == 1:
        print_table(["Technology", "Candidates"], r.candidate_count_by_technology())
    elif choice == 2:
        print_table(*r.placement_summary())
    elif choice == 3:
        print_table(*r.company_wise_placements())
    elif choice == 4:
        print_table(*r.applications_by_status())
    elif choice == 5:
        print_table(*r.job_wise_applications())
    elif choice == 6:
        print_table(*r.upcoming_interviews())
    elif choice == 7:
        print_table(*r.offers_by_status())
    elif choice == 8:
        print_table(*r.highest_package_placements(ask_int("How many records")))
    elif choice == 9:
        print_table(*r.technology_wise_placements())
    elif choice == 10:
        print_table(*r.not_placed_candidates())


# ------------------------------------------------------------------ wiring

class AppContext:
    """Creates every DAO and service once (Main -> Service -> DAO -> MySQL)."""

    def __init__(self):
        candidate_dao = CandidateDAO()
        company_dao = CompanyDAO()
        job_dao = JobDAO()
        self.application_dao = ApplicationDAO()
        interview_dao = InterviewDAO()
        offer_dao = OfferDAO()
        placement_dao = PlacementDAO()

        self.eligibility = EligibilityService()
        self.candidates = CandidateService(candidate_dao)
        self.companies = CompanyService(company_dao)
        self.jobs = JobService(job_dao, company_dao)
        self.applications = ApplicationService(
            candidate_dao, job_dao, self.application_dao, self.eligibility
        )
        self.interviews = InterviewService(self.application_dao, interview_dao)
        self.offers = OfferService(
            self.application_dao, job_dao, offer_dao, placement_dao
        )
        self.placements = PlacementService(placement_dao, offer_dao)
        self.reports = ReportService()
        self.log = ActivityLogService()


MENUS = {
    1: candidate_menu,
    2: company_menu,
    3: job_menu,
    4: application_menu,
    5: interview_menu,
    6: offer_menu,
    7: placement_menu,
    8: report_menu,
}


def main():
    ctx = AppContext()

    while True:
        print_menu()

        try:
            choice = int(input("Enter Your Choice: "))

            if choice == 9:
                print("Application closed.")
                break

            handler = MENUS.get(choice)
            if handler:
                handler(ctx)
            else:
                print("Invalid choice.")

        except ValueError as exc:
            print("ERROR: invalid input -", exc)
        except Exception as exc:
            print("ERROR:", exc)


if __name__ == "__main__":
    main()
