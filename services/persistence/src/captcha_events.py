"""
CAPTCHA Events Repository
Tracks CAPTCHA challenges and solving attempts
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from .database import get_db

logger = logging.getLogger(__name__)


class CaptchaEventsRepository:
    """Handles CAPTCHA event tracking"""

    def __init__(self):
        self.db = get_db()

    def log_captcha_event(
        self,
        application_id: UUID,
        provider: str,
        attempt_number: int = 1,
        status: str = 'attempted',
        solver_type: Optional[str] = None
    ) -> UUID:
        """
        Log a CAPTCHA event.

        Args:
            application_id: Application ID
            provider: CAPTCHA provider (hcaptcha, recaptcha_v2, etc.)
            attempt_number: Attempt number
            status: attempted, solved, failed, skipped
            solver_type: agent, human, external_service, 2captcha

        Returns:
            Event ID
        """
        query = """
            INSERT INTO captcha_events (
                application_id, provider, attempt_number, status, solver_type
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (application_id, provider, attempt_number, status, solver_type)
        )

        event_id = result[0]['id']
        logger.info(f"Logged CAPTCHA event {event_id} for application {application_id} (status: {status})")
        return event_id

    def get_captcha_events(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Get all CAPTCHA events for an application"""
        query = """
            SELECT * FROM captcha_events
            WHERE application_id = %s
            ORDER BY created_at ASC
        """
        return self.db.execute_query(query, (application_id,))

    def update_captcha_status(self, event_id: UUID, status: str):
        """Update CAPTCHA event status"""
        query = """
            UPDATE captcha_events
            SET status = %s
            WHERE id = %s
        """
        self.db.execute_query(query, (status, event_id), fetch=False)


class TwoFactorEventsRepository:
    """Handles 2FA event tracking"""

    def __init__(self):
        self.db = get_db()

    def log_2fa_request(
        self,
        application_id: UUID,
        method: str,
        status: str = 'pending',
        notes: Optional[str] = None
    ) -> UUID:
        """
        Log a 2FA request.

        Args:
            application_id: Application ID
            method: 2FA method (sms, email, app)
            status: pending, completed, failed, skipped
            not es: Additional notes

        Returns:
            Event ID
        """
        query = """
            INSERT INTO two_factor_events (
                application_id, method, status, notes, requested_at
            )
            VALUES (%s, %s, %s, %s, now())
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (application_id, method, status, notes)
        )

        event_id = result[0]['id']
        logger.info(f"Logged 2FA request {event_id} for application {application_id}")
        return event_id

    def mark_2fa_completed(self, event_id: UUID, status: str = 'completed'):
        """Mark 2FA as completed"""
        query = """
            UPDATE two_factor_events
            SET status = %s, code_supplied_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (status, event_id), fetch=False)

    def get_2fa_events(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Get all 2FA events for an application"""
        query = """
            SELECT * FROM two_factor_events
            WHERE application_id = %s
            ORDER BY requested_at ASC
        """
        return self.db.execute_query(query, (application_id,))
