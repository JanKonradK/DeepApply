# Persistence Service

The Data Access Layer for Nyx Venatrix. This module provides a clean abstraction over the PostgreSQL database, handling all CRUD operations and data integrity.

## Modules

### `src/database.py`
Manages the PostgreSQL connection pool (using `psycopg2` and `DBUtils`) and provides transaction management utilities.

### `src/jobs.py`
Repositories for:
- `JobPost`: Storing job descriptions, metadata, and embeddings.
- `Company`: Managing company entities and their tiers (Top, Normal, Avoid).
- `JobSource`: Tracking where jobs were found.

### `src/users.py`
Repositories for:
- `User`: User identity management.
- `UserProfile`: Storing skills, experience, and preferences.
- `Resume`: Managing resume versions and files.

### `src/applications.py`
Repositories for:
- `Application`: Tracking the state of each application (Started, Submitted, Failed).
- `ApplicationHistory`: Audit log of status changes.

### `src/sessions.py`
Repositories for:
- `ApplicationSession`: Managing batch runs.
- `SessionDigest`: Storing summary statistics for sessions.

### `src/events.py`
Repositories for:
- `EventLog`: Centralized logging for all system events (CAPTCHAs, Errors, Successes).

## Usage

This module is intended to be imported by the Agent service.

```python
from persistence.src.jobs import JobRepository
from persistence.src.database import get_db

repo = JobRepository()
job = repo.get_job_post(job_id)
```
