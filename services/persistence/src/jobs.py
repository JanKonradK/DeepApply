"""
Job & Company Persistence Operations
CRUD operations for job_posts, companies, job_sources, job_tags
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

from .database import get_db

logger = logging.getLogger(__name__)


class JobRepository:
    """Handles all job-related database operations"""

    def __init__(self):
        self.db = get_db()

    def create_job_post(
        self,
        source_url: str,
        job_source_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        canonical_url: Optional[str] = None,
        job_title: Optional[str] = None,
        location_city: Optional[str] = None,
        location_country: Optional[str] = None,
        description_clean: Optional[str] = None,
        embedding_vector_id: Optional[str] = None,
        is_remote_allowed: bool = False
    ) -> UUID:
        """Create a new job post record"""
        query = """
            INSERT INTO job_posts (
                source_url, job_source_id, company_id, canonical_url, job_title,
                location_city, location_country, description_clean,
                embedding_vector_id, is_remote_allowed
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (source_url, job_source_id, company_id, canonical_url, job_title,
             location_city, location_country, description_clean,
             embedding_vector_id, is_remote_allowed)
        )

        job_id = result[0]['id']
        logger.info(f"Created job post {job_id}: {job_title}")
        return job_id

    def get_job_post(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        """Get job post by ID"""
        query = "SELECT * FROM job_posts WHERE id = %s"
        result = self.db.execute_query(query, (job_id,))
        return result[0] if result else None

    def update_job_post(
        self,
        job_id: UUID,
        company_id: Optional[UUID] = None,
        job_title: Optional[str] = None,
        description_clean: Optional[str] = None,
        embedding_vector_id: Optional[str] = None
    ):
        """Update job post fields"""
        updates = []
        params = []

        if company_id is not None:
            updates.append("company_id = %s")
            params.append(company_id)
        if job_title is not None:
            updates.append("job_title = %s")
            params.append(job_title)
        if description_clean is not None:
            updates.append("description_clean = %s")
            params.append(description_clean)
        if embedding_vector_id is not None:
            updates.append("embedding_vector_id = %s")
            params.append(embedding_vector_id)

        if updates:
            updates.append("updated_at = now()")
            params.append(job_id)

            query = f"""
                UPDATE job_posts
                SET {', '.join(updates)}
                WHERE id = %s
            """
            self.db.execute_query(query, tuple(params), fetch=False)

    def get_or_create_company(
        self,
        name: str,
        canonical_domain: Optional[str] = None,
        tier: str = 'normal'
    ) -> UUID:
        """Get existing company or create new one"""
        # Try to find by domain first
        if canonical_domain:
            query = "SELECT id FROM companies WHERE canonical_domain = %s"
            result = self.db.execute_query(query, (canonical_domain,))
            if result:
                return result[0]['id']

        # Try to find by name
        query = "SELECT id FROM companies WHERE name = %s"
        result = self.db.execute_query(query, (name,))
        if result:
            return result[0]['id']

        # Create new company
        query = """
            INSERT INTO companies (name, canonical_domain, tier)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        result = self.db.execute_query(query, (name, canonical_domain, tier))
        company_id = result[0]['id']
        logger.info(f"Created company {company_id}: {name}")
        return company_id

    def get_company(self, company_id: UUID) -> Optional[Dict[str, Any]]:
        """Get company by ID"""
        query = "SELECT * FROM companies WHERE id = %s"
        result = self.db.execute_query(query, (company_id,))
        return result[0] if result else None

    def update_company_tier(self, company_id: UUID, tier: str):
        """Update company tier (top/normal/avoid)"""
        query = """
            UPDATE companies
            SET tier = %s, updated_at = now()
            WHERE id = %s
        """
        self.db.execute_query(query, (tier, company_id), fetch=False)

    def get_or_create_job_source(self, name: str, source_type: str = 'job_board') -> UUID:
        """Get existing job source or create new one"""
        query = "SELECT id FROM job_sources WHERE name = %s"
        result = self.db.execute_query(query, (name,))

        if result:
            return result[0]['id']

        query = """
            INSERT INTO job_sources (name, source_type)
            VALUES (%s, %s)
            RETURNING id
        """
        result = self.db.execute_query(query, (name, source_type))
        return result[0]['id']

    def add_tag_to_job(self, job_post_id: UUID, tag_name: str, category: str = 'skill'):
        """Add a tag to a job post"""
        # Get or create tag
        tag_query = """
            INSERT INTO job_tags (name, category)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """
        tag_result = self.db.execute_query(tag_query, (tag_name, category))
        tag_id = tag_result[0]['id']

        # Link to job
        link_query = """
            INSERT INTO job_post_tags (job_post_id, job_tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """
        self.db.execute_query(link_query, (job_post_id, tag_id), fetch=False)

    def get_job_tags(self, job_post_id: UUID) -> List[str]:
        """Get all tags for a job"""
        query = """
            SELECT jt.name
            FROM job_tags jt
            JOIN job_post_tags jpt ON jt.id = jpt.job_tag_id
            WHERE jpt.job_post_id = %s
        """
        results = self.db.execute_query(query, (job_post_id,))
        return [r['name'] for r in results]
