# Project Cleanup & Structure Audit

## ✅ Actions Taken
1.  **Removed Redundant Files**:
    - `tests/dummy_resume.pdf` (Replaced with `profile_data/CVs/john_doe.pdf`)
    - `tests/pipeline_flow.py` (Redundant test script)
2.  **Updated Test Scripts**:
    - `tests/simulation_run.py` now uses the real profile resume.
    - `tests/e2e_workflow.py` now uses the real profile resume.

## 📂 File Structure Audit

### Core Services (`services/`)
- `agent/`: Contains all agent logic (orchestrator, form filler, planning).
- `backend/`: API backend (FastAPI).
- `persistence/`: Database repositories and schema.

### Testing (`tests/`)
- `e2e_workflow.py`: Main end-to-end test.
- `simulation_run.py`: Multi-agent simulation.
- `production_demo.py`: Quick verification script.
- `example_target_site.html`: Local test target.

### Configuration
- `profile_data/`: User profiles and resumes.
- `config/`: Application configuration (effort policy, etc.).
- `infrastructure/`: Docker and database setup.

## 🗑️ Potential Redundancies
The following files might be candidates for removal if not actively used:

1.  `tests/captcha_fallback_test.py`: Small test script, potentially covered by `test_advanced_features.py`.
2.  `tests/test_chrome_cdp.py`: If we are using `browser-use` or Playwright directly, raw CDP tests might be obsolete.

## 📝 Recommendations
1.  **Consolidate Tests**: Move standalone test scripts into the `tests/` suite using `pytest`.
2.  **Standardize Resume Location**: Ensure all new tests reference `profile_data/CVs/`.
