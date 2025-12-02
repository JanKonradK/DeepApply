"""
Domain Rate Limiting Repository
Tracks and enforces per-domain application limits
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from uuid import UUID

from .database import get_db

logger = logging.getLogger(__name__)


class DomainRateLimitRepository:
    """Manages domain-specific rate limits and blocking"""

    def  __init__(self):
        self.db = get_db()

    def record_application(
        self,
        domain_name: str,
        success: bool
    ) -> None:
        """
        Record an application attempt for a domain.

        Args:
            domain_name: Domain name (e.g., 'linkedin.com')
            success: Whether the application was successful
        """
        today = date.today()

        # Insert or update today's stats
        query = """
            INSERT INTO domain_rate_limits (domain_name, date, applications_attempted, applications_successful, applications_failed)
            VALUES (%s, %s, 1, %s, %s)
            ON CONFLICT (domain_name, date)
            DO UPDATE SET
                applications_attempted = domain_rate_limits.applications_attempted + 1,
                applications_successful = domain_rate_limits.applications_successful + EXCLUDED.applications_successful,
                applications_failed = domain_rate_limits.applications_failed + EXCLUDED.applications_failed
        """

        successful_count = 1 if success else 0
        failed_count = 0 if success else 1

        self.db.execute_query(query, (domain_name, today, successful_count, failed_count), fetch=False)
        logger.info(f"Recorded application for {domain_name} (success: {success})")

    def get_today_stats(self, domain_name: str) -> Dict[str, Any]:
        """Get today's stats for a domain"""
        today = date.today()

        query = """
            SELECT * FROM domain_rate_limits
            WHERE domain_name = %s AND date = %s
        """

        result = self.db.execute_query(query, (domain_name, today))

        if result:
            return result[0]
        else:
            return {
                'domain_name': domain_name,
                'date': today,
                'applications_attempted': 0,
                'applications_successful': 0,
                'applications_failed': 0,
                'is_temporarily_blocked': False
            }

    def mark_blocked(
        self,
        domain_name: str,
        block_duration_hours: int = 24,
        reason: Optional[str] = None
    ) -> None:
        """
        Mark a domain as temporarily blocked.

        Args:
            domain_name: Domain to block
            block_duration_hours: How long to block (hours)
            reason: Reason for blocking
        """
        today = date.today()
        blocked_until = datetime.now() + timedelta(hours=block_duration_hours)

        query = """
            INSERT INTO domain_rate_limits (domain_name, date, is_temporarily_blocked, blocked_until, last_block_timestamp, notes)
            VALUES (%s, %s, true, %s, now(), %s)
            ON CONFLICT (domain_name, date)
            DO UPDATE SET
                is_temporarily_blocked = true,
                blocked_until = EXCLUDED.blocked_until,
                last_block_timestamp = now(),
                notes = EXCLUDED.notes
        """

        self.db.execute_query(query, (domain_name, today, blocked_until, reason), fetch=False)
        logger.warning(f"Domain {domain_name} blocked until {blocked_until} - Reason: {reason}")

    def is_blocked(self, domain_name: str) -> bool:
        """Check if a domain is currently blocked"""
        stats = self.get_today_stats(domain_name)

        if not stats.get('is_temporarily_blocked'):
            return False

        # Check if block has expired
        blocked_until = stats.get('blocked_until')
        if blocked_until and datetime.now() > blocked_until:
            # Unblock
            self.unblock_domain(domain_name)
            return False

        return True

    def unblock_domain(self, domain_name: str) -> None:
        """Unblock a domain"""
        today = date.today()

        query = """
            UPDATE domain_rate_limits
            SET is_temporarily_blocked = false, blocked_until = NULL
            WHERE domain_name = %s AND date = %s
        """

        self.db.execute_query(query, (domain_name, today), fetch=False)
        logger.info(f"Domain {domain_name} unblocked")


class DomainPolicyRepository:
    """Manages domain-specific policies"""

    def __init__(self):
        self.db = get_db()

    def get_policy(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get policy for a domain"""
        query = """
            SELECT * FROM domain_policies
            WHERE domain_name = %s
        """

        result = self.db.execute_query(query, (domain_name,))
        return result[0] if result else None

    def create_or_update_policy(
        self,
        domain_name: str,
        max_applications_per_day: Optional[int] = None,
        min_seconds_between_applications: Optional[int] = None,
        max_concurrent_applications: int = 1,
        avoid_if_possible: bool = False,
        notes: Optional[str] = None
    ) -> None:
        """Create or update a domain policy"""
        query = """
            INSERT INTO domain_policies (
                domain_name, max_applications_per_day, min_seconds_between_applications,
                max_concurrent_applications, avoid_if_possible, notes, last_reviewed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, now())
            ON CONFLICT (domain_name)
            DO UPDATE SET
                max_applications_per_day = EXCLUDED.max_applications_per_day,
                min_seconds_between_applications = EXCLUDED.min_seconds_between_applications,
                max_concurrent_applications = EXCLUDED.max_concurrent_applications,
                avoid_if_possible = EXCLUDED.avoid_if_possible,
                notes = EXCLUDED.notes,
                last_reviewed_at = now()
        """

        self.db.execute_query(
            query,
            (domain_name, max_applications_per_day, min_seconds_between_applications,
             max_concurrent_applications, avoid_if_possible, notes),
            fetch=False
        )

        logger.info(f"Policy updated for {domain_name}")

    def should_apply_to_domain(
        self,
        domain_name: str,
        current_attempts_today: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check if we should apply to this domain.

        Returns:
            (should_apply, reason)
        """
        policy = self.get_policy(domain_name)

        if not policy:
            return True, None

        # Check if domain should be avoided
        if policy.get('avoid_if_possible'):
            return False, "Domain marked as 'avoid if possible'"

        # Check daily limit
        max_daily = policy.get('max_applications_per_day')
        if max_daily and current_attempts_today >= max_daily:
            return False, f"Daily limit reached ({max_daily})"

        return True, None
