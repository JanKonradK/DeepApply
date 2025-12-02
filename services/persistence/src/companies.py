from typing import Dict, Any, Optional, List
from uuid import UUID
import logging
from psycopg2.extras import Json
from .database import get_db

logger = logging.getLogger(__name__)

class CompanyRepository:
    def __init__(self):
        self.conn = get_db()

    def get_by_id(self, company_id: UUID) -> Optional[Dict[str, Any]]:
        """Get company by ID."""
        with self.conn.get_cursor() as cur:
            cur.execute(
                "SELECT * FROM companies WHERE id = %s",
                (str(company_id),)
            )
            return cur.fetchone()

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get company by name (case insensitive match)."""
        with self.conn.get_cursor() as cur:
            cur.execute(
                "SELECT * FROM companies WHERE LOWER(name) = LOWER(%s)",
                (name,)
            )
            return cur.fetchone()

    def create_or_update(self, name: str, domain: Optional[str] = None, tier: str = 'normal') -> UUID:
        """Create or update a company record."""
        with self.conn.get_cursor() as cur:
            # Check if exists by domain first if provided
            if domain:
                cur.execute("SELECT id FROM companies WHERE canonical_domain = %s", (domain,))
                res = cur.fetchone()
                if res:
                    return res['id']

            # Check by name
            cur.execute("SELECT id FROM companies WHERE LOWER(name) = LOWER(%s)", (name,))
            res = cur.fetchone()
            if res:
                return res['id']

            # Create new
            cur.execute(
                """
                INSERT INTO companies (name, canonical_domain, tier)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (name, domain, tier)
            )
            return cur.fetchone()['id']

    def update_stats(self, company_id: UUID, stats: Dict[str, Any]):
        """Update company statistics/properties."""
        with self.conn.get_cursor() as cur:
            for key, value in stats.items():
                cur.execute(
                    """
                    INSERT INTO company_properties (company_id, key, value)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (company_id, key)
                    DO UPDATE SET value = EXCLUDED.value, updated_at = now()
                    """,
                    (str(company_id), key, Json(value))
                )
