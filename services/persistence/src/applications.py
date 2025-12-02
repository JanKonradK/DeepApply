"""
Application Persistence Operations
CRUD operations for applications, application_status_history, application_questions, application_steps
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

from .database import get_db

logger = logging.getLogger(__name__)


class ApplicationRepository:
    """Handles all application-related database operations"""

    def __init__(self):
        self.db = get_db()

    def create_application(
        self,
        user_id: UUID,
        job_post_id: UUID,
        effort_level: str = 'medium',
        session_id: Optional[UUID] = None,
        match_score: Optional[float] = None,
        selected_resume_version_id: Optional[UUID] = None,
        profile_id: Optional[UUID] = None
    ) -> UUID:
        """Create a new application record"""
        query = """
            INSERT INTO applications (
                user_id, job_post_id, session_id, effort_level, match_score,
                selected_resume_version_id, profile_id, application_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'queued')
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (user_id, job_post_id, session_id, effort_level, match_score,
             selected_resume_version_id, profile_id)
        )

        app_id = result[0]['id']
        logger.info(f"Created application {app_id} for job {job_post_id}")
        return app_id

    def get_application(self, application_id: UUID) -> Optional[Dict[str, Any]]:
        """Get application by ID"""
        query = "SELECT * FROM applications WHERE id = %s"
        result = self.db.execute_query(query, (application_id,))
        return result[0] if result else None

    def update_status(
        self,
        application_id: UUID,
        new_status: str,
        reason: Optional[str] = None,
        actor: str = 'system'
    ):
        """Update application status and log to history"""
        # Get current status
        current = self.get_application(application_id)
        if not current:
            raise ValueError(f"Application {application_id} not found")

        old_status = current['application_status']

        # Update status
        query = """
            UPDATE applications
            SET application_status = %s, updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (new_status, application_id), fetch=False)

        # Log to history
        history_query = """
            INSERT INTO application_status_history (
                application_id, old_status, new_status, reason, actor
            )
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(
            history_query,
            (application_id, old_status, new_status, reason, actor),
            fetch=False
        )

        logger.info(f"Application {application_id} status: {old_status} → {new_status}")

    def mark_started(self, application_id: UUID):
        """Mark application as started"""
        query = """
            UPDATE applications
            SET application_status = 'in_progress',
                application_started_at = now(),
                updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (application_id,), fetch=False)
        logger.info(f"Application {application_id} marked as started")

    def mark_submitted(
        self,
        application_id: UUID,
        success_flag: bool = True,
        confirmation_type: Optional[str] = None,
        confirmation_screenshot_path: Optional[str] = None
    ):
        """Mark application as submitted"""
        query = """
            UPDATE applications
            SET application_status = 'submitted',
                application_submitted_at = now(),
                success_flag = %s,
                final_confirmation_type = %s,
                final_confirmation_screenshot_path = %s,
                updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(
            query,
            (success_flag, confirmation_type, confirmation_screenshot_path, application_id),
            fetch=False
        )

        reason = f"Submitted successfully ({confirmation_type or 'unknown'})"
        self.update_status(application_id, 'submitted', reason)

    def mark_failed(
        self,
        application_id: UUID,
        failure_reason_code: str,
        failure_reason_detail: Optional[str] = None,
        manual_followup_needed: bool = False
    ):
        """Mark application as failed"""
        query = """
            UPDATE applications
            SET application_status = 'failed',
                failure_reason_code = %s,
                failure_reason_detail = %s,
                manual_followup_needed = %s,
                updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(
            query,
            (failure_reason_code, failure_reason_detail, manual_followup_needed, application_id),
            fetch=False
        )

        self.update_status(application_id, 'failed', f"Failed: {failure_reason_code}")

    def set_observability_ids(
        self,
        application_id: UUID,
        mlflow_run_id: Optional[str] = None,
        langfuse_trace_id: Optional[str] = None
    ):
        """Set MLflow and Langfuse IDs"""
        query = """
            UPDATE applications
            SET mlflow_run_id = COALESCE(%s, mlflow_run_id),
                langfuse_trace_id = COALESCE(%s, langfuse_trace_id),
                updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (mlflow_run_id, langfuse_trace_id, application_id), fetch=False)

    def update_metrics(
        self,
        application_id: UUID,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        cost_estimated: Optional[float] = None
    ):
        """Update token and cost metrics"""
        updates = []
        params = []

        if tokens_input is not None:
            updates.append("tokens_input_total = tokens_input_total + %s")
            params.append(tokens_input)
        if tokens_output is not None:
            updates.append("tokens_output_total = tokens_output_total + %s")
            params.append(tokens_output)
        if cost_estimated is not None:
            updates.append("cost_estimated_total = cost_estimated_total + %s")
            params.append(cost_estimated)

        if updates:
            updates.append("updated_at = now()")
            params.append(application_id)

            query = f"""
                UPDATE applications
                SET {', '.join(updates)}
                WHERE id = %s
            """
            self.db.execute_query(query, tuple(params), fetch=False)

    def log_question(
        self,
        application_id: UUID,
        step_index: int,
        field_type: str,
        field_label_raw: Optional[str] = None,
        field_name_attr: Optional[str] = None,
        is_required: bool = False,
        value_filled: Optional[str] = None,
        value_source: str = 'profile',
        confidence_score: Optional[float] = None
    ) -> UUID:
        """Log a filled question/field"""
        query = """
            INSERT INTO application_questions (
                application_id, step_index, field_type, field_label_raw,
                field_name_attr, is_required, value_filled, value_source,
                confidence_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (application_id, step_index, field_type, field_label_raw, field_name_attr,
             is_required, value_filled, value_source, confidence_score)
        )

        return result[0]['id']

    def get_questions(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Get all questions for an application"""
        query = """
            SELECT * FROM application_questions
            WHERE application_id = %s
            ORDER BY step_index ASC
        """
        return self.db.execute_query(query, (application_id,))

    def correct_question(
        self,
        question_id: UUID,
        corrected_value: str,
        corrected_by: str = 'qa_agent'
    ):
        """Apply QA correction to a question"""
        query = """
            UPDATE application_questions
            SET corrected_value = %s,
                corrected_by = %s,
                updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (corrected_value, corrected_by, question_id), fetch=False)

    def log_step(
        self,
        application_id: UUID,
        step_index: int,
        action_type: str,
        description: Optional[str] = None,
        page_url: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> UUID:
        """Log an agent step"""
        query = """
            INSERT INTO application_steps (
                application_id, step_index, action_type, description,
                page_url, timestamp_end, success, error_message
            )
            VALUES (%s, %s, %s, %s, %s, now(), %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (application_id, step_index, action_type, description, page_url, success, error_message)
        )

        return result[0]['id']

    def get_queued_applications(self, session_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get queued applications for a session"""
        query = """
            SELECT * FROM applications
            WHERE session_id = %s AND application_status = 'queued'
            ORDER BY created_at ASC
            LIMIT %s
        """
        return self.db.execute_query(query, (session_id, limit))
