# Recruitment & Placement Management System (RPMS)

A console-based **Python + MySQL** application that manages the full campus
recruitment cycle: candidates, companies, jobs, applications, interviews,
offers and placements, with reports.

**Architecture:** `Main (menu) -> Service (business rules) -> DAO (SQL) -> MySQL`

## Modules

| # | Module | What it does |
|---|--------|--------------|
| 1 | Candidate Management | Add / view / search candidates with validation (email, mobile, percentage, duplicates) |
| 2 | Company Management | Add, update, activate/deactivate companies |
| 3 | Job Management | Post jobs for active companies, close jobs, list by company |
| 4 | Eligibility Check | Percentage, passing year, backlogs, deadline, job/profile status |
| 5 | Job Application | Apply for a job (duplicate + eligibility checks), view applications |
| 6 | Interview Management | Schedule rounds, reschedule, cancel, no-show, feedback and ratings |
| 7 | Offer Management | Create offers for selected candidates, accept / reject / expire / withdraw |
| 8 | Placement Management | Created on offer acceptance; record joining, defer, not-joined |
| 9 | Reports | 9 reports (placement summary, company-wise, top packages, and more) |

## Application status flow

```
APPLIED -> INTERVIEW_SCHEDULED -> INTERVIEWED -> SELECTED -> OFFERED -> JOINED
                                      |              |          |
                                  (next round)   REJECTED    WITHDRAWN / REJECTED
```

- Interview feedback sets the application to `INTERVIEWED`, `SELECTED` or `REJECTED`.
- An offer can only be created when the application is `SELECTED`.
- Accepting an offer creates the placement and marks the candidate `PLACED`.
- Recording the joining sets the application to `JOINED`.
- Not joining cancels the placement and frees the candidate again.
- Multi-table actions run in a single database transaction (all or nothing).

## Project structure

```
RPMS_Python_VSCode/
├── main.py                  # entry point
├── requirements.txt
├── sql/                     # rpms_schema.sql, rpms_sample_data.sql, rpms_full_setup.sql
├── docs/Python_Project_Scope.txt
└── rpms/
    ├── app/main.py          # console menus
    ├── model/               # dataclasses (Candidate, Company, Job, Application, Interview, Offer, Placement)
    ├── dao/                 # database access (one DAO per entity)
    ├── service/             # business rules + reports
    ├── exception/           # custom exceptions
    └── util/                # DB connection, validation, table display
```

## How to run

1. Install **Python 3.10+** and **MySQL 8**.
2. Create the database (this also loads sample data):

   ```bash
   mysql -u root -p < sql/rpms_full_setup.sql
   ```

3. Create a virtual environment and install the dependency:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # Linux / macOS
   pip install -r requirements.txt
   ```

4. Set your MySQL password. Either edit `rpms/util/db_connection.py`, or set an
   environment variable (recommended, so the password is not pushed to GitHub):

   ```bash
   set RPMS_DB_PASSWORD=your_password        # Windows
   # export RPMS_DB_PASSWORD=your_password   # Linux / macOS
   ```

   Optional variables: `RPMS_DB_HOST`, `RPMS_DB_PORT`, `RPMS_DB_USER`, `RPMS_DB_NAME`.

5. Run:

   ```bash
   python main.py
   ```

## Sample walkthrough (end to end)

1. **Candidates -> View** to find a candidate ID.
2. **Job Application -> Apply for Job** (candidate ID + open job ID).
3. **Interview -> Schedule**, then **Submit Feedback** with `SELECTED`.
4. **Offer -> Create Offer** for that application, then **Accept Offer**.
5. **Placement -> Record Joining**.
6. **Reports -> Placement Summary**.

Sample data uses user IDs 1-5 (for example, 2 is a recruiter) wherever the
menu asks for a "User ID". Some sample jobs have deadlines that may already have
passed; add a new job with a future deadline from **Job Management** to test applying.

## Activity log

Every create/update action is appended to `activity_log.txt` with a timestamp.
