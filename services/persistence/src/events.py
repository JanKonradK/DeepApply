"""
Event Persistence Operations
CRUD operations for application_events, captcha_events, two_factor_events
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

from .database import get_db

logger = logging.getLogger(__name__)


class EventRepository:
    """Handles all event-related database operations"""

    def __init__(self):
        self.db = get_db()

    def append_event(
        self,
        event_type: str,
        application_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        event_detail: Optional[str] = None,
        payload: Optional[Dict] = None
    ) -> UUID:
        """Append event to application_events"""
        import json

        query = """
            INSERT INTO application_events (
                application_id, session_id, event_type, event_detail, payload
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (application_id, session_id, event_type, event_detail, json.dumps(payload or {}))
        )

        event_id = result[0]['id']
        logger.info(f"Logged event: {event_type} (app: {application_id}, session: {session_id})")
        return event_id

    def get_events(
        self,
        application_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events with optional filters"""
        conditions = []
        params = []

        if application_id:
            conditions.append("application_id = %s")
            params.append(application_id)
        if session_id:
            conditions.append("session_id = %s")
            params.append(session_id)
        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        query = f"""
            SELECT * FROM application_events
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """

        return self.db.execute_query(query, tuple(params))

    def log_captcha_event(
        self,
        application_id: UUID,
        provider: str,
        attempt_number: int = 1,
        status: str = 'attempted',
        solver_type: Optional[str] = None
    ) -> UUID:
        """Log CAPTCHA event"""
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
        logger.info(f"CAPTCHA event: {provider} - {status} (app: {application_id})")

        # Also log to general events
        self.append_event(
            f"captcha_{status}",
            application_id=application_id,
            event_detail=f"{provider} captcha {status}",
            payload={'provider': provider, 'attempt': attempt_number, 'solver': solver_type}
        )

        return event_id

    def get_captcha_events(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Get all CAPTCHA events for an application"""
        query = """
            SELECT * FROM captcha_events
            WHERE application_id = %s
            ORDER BY created_at ASC
        """
        return self.db.execute_query(query, (application_id,))

    def log_2fa_event(
        self,
        application_id: UUID,
        method: str,
        status: str = 'pending',
        notes: Optional[str] = None
    ) -> UUID:
        """Log 2FA event"""
        query = """
            INSERT INTO two_factor_events (
                application_id, method, status, notes
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (application_id, method, status, notes)
        )

        event_id = result[0]['id']
        logger.info(f"2FA event: {method} - {status} (app: {application_id})")

        # Also log to general events
        self.append_event(
            f"two_factor_{status}",
            application_id=application_id,
            event_detail=f"2FA {method} {status}",
            payload={'method': method, 'notes': notes}
        )

        return event_id

    def update_2fa_supplied(self, event_id: UUID):
        """Mark 2FA code as supplied"""
        query = """
            UPDATE two_factor_events
            SET status = 'completed',
                code_supplied_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (event_id,), fetch=False)

    def get_2fa_events(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Get all 2FA events for an application"""
        query = """
            SELECT * FROM two_factor_events
            WHERE application_id = %s
            ORDER BY requested_at ASC
        """
        return self.db.execute_query(query, (application_id,))
