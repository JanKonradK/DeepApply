"""
User & Profile Persistence Operations
CRUD operations for users, user_profiles, resumes, resume_versions
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

from .database import get_db

logger = logging.getLogger(__name__)


class UserRepository:
    """Handles all user-related database operations"""

    def __init__(self):
        self.db = get_db()

    def create_user(
        self,
        name: str,
        email: str,
        external_id: Optional[str] = None,
        timezone: str = 'UTC'
    ) -> UUID:
        """Create a new user"""
        query = """
            INSERT INTO users (name, email, external_id, timezone, is_active)
            VALUES (%s, %s, %s, %s, true)
            RETURNING id
        """

        result = self.db.execute_query(query, (name, email, external_id, timezone))
        user_id = result[0]['id']
        logger.info(f"Created user {user_id}: {name}")
        return user_id

    def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None

    def create_profile(
        self,
        user_id: UUID,
        profile_name: str,
        headline: Optional[str] = None,
        summary_text: Optional[str] = None,
        skills_true: Optional[List[str]] = None,
        skills_false: Optional[List[str]] = None,
        languages: Optional[List[Dict]] = None
    ) -> UUID:
        """Create a user profile"""
        import json

        query = """
            INSERT INTO user_profiles (
                user_id, profile_name, headline, summary_text,
                skills_true, skills_false, languages, is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, true)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (user_id, profile_name, headline, summary_text,
             json.dumps(skills_true or []),
             json.dumps(skills_false or []),
             json.dumps(languages or []))
        )

        profile_id = result[0]['id']
        logger.info(f"Created profile {profile_id}: {profile_name}")
        return profile_id

    def get_profile(self, profile_id: UUID) -> Optional[Dict[str, Any]]:
        """Get profile by ID"""
        query = "SELECT * FROM user_profiles WHERE id = %s"
        result = self.db.execute_query(query, (profile_id,))
        return result[0] if result else None

    def get_user_profiles(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all profiles for a user"""
        query = """
            SELECT * FROM user_profiles
            WHERE user_id = %s AND is_active = true
            ORDER BY created_at DESC
        """
        return self.db.execute_query(query, (user_id,))

    def create_resume(
        self,
        user_profile_id: UUID,
        resume_key: str,
        display_name: str,
        description: Optional[str] = None
    ) -> UUID:
        """Create a resume record"""
        query = """
            INSERT INTO resumes (
                user_profile_id, resume_key, display_name, description, is_active
            )
            VALUES (%s, %s, %s, %s, true)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (user_profile_id, resume_key, display_name, description)
        )

        resume_id = result[0]['id']
        logger.info(f"Created resume {resume_id}: {resume_key}")
        return resume_id

    def create_resume_version(
        self,
        resume_id: UUID,
        version_number: int,
        source_format: str,
        file_path: str,
        content_text: Optional[str] = None,
        content_hash: Optional[str] = None,
        is_default: bool = False
    ) -> UUID:
        """Create a resume version"""
        import hashlib

        # Generate content hash if not provided
        if content_hash is None and content_text:
            content_hash = hashlib.sha256(content_text.encode()).hexdigest()

        query = """
            INSERT INTO resume_versions (
                resume_id, version_number, source_format, file_path,
                content_text, content_hash, is_default_for_resume
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (resume_id, version_number, source_format, file_path,
             content_text, content_hash, is_default)
        )

        version_id = result[0]['id']
        logger.info(f"Created resume version {version_id} for resume {resume_id}")
        return version_id

    def get_default_resume_version(self, resume_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the default version for a resume"""
        query = """
            SELECT * FROM resume_versions
            WHERE resume_id = %s AND is_default_for_resume = true
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = self.db.execute_query(query, (resume_id,))
        return result[0] if result else None

    def get_resume_versions(self, resume_id: UUID) -> List[Dict[str, Any]]:
        """Get all versions for a resume"""
        query = """
            SELECT * FROM resume_versions
            WHERE resume_id = %s
            ORDER BY version_number DESC
        """
        return self.db.execute_query(query, (resume_id,))
