import os
import sqlite3
from datetime import datetime
import pandas as pd

from app.logger import logger
from app.config import DB_PATH


class JobDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

        # Ensure directory exists (if you’re using nested paths)
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)

        self.job_columns = [
            "id",
            "title",
            "PositionURI",
            "company",
            "location",
            "category",
            "career_level",
            "start_date",
            "description",
            "requirements",
            "posted_at",
            "score",
            "reason",
            "PublicationStartDate",
            "PublicationEndDate",
        ]

        self.conn = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def _create_table(self):
        """Create jobs table if it doesn't exist"""
        try:
            create_sql = """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    PositionURI TEXT,
                    company TEXT,
                    location TEXT,
                    category TEXT,
                    career_level TEXT,
                    start_date TEXT,
                    description TEXT,
                    requirements TEXT,
                    fetched_at TEXT NOT NULL,
                    score TEXT,
                    reason INTEGER,
                    eval_option TEXT,
                    PublicationStartDate TEXT,
                    PublicationEndDate TEXT,
                    UNIQUE(id)
                )
            """
            self.conn.execute(create_sql)
            self.conn.commit()

            # Verify table was created
            cursor = self.conn.execute("PRAGMA table_info(jobs)")
            columns = [row[1] for row in cursor.fetchall()]
            logger.info(f"Jobs table columns: {columns}")

        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise

    def insert_or_ignore(self, job):
        """Insert job into database, ignore if exists"""
        try:
            insert_sql = """
                INSERT OR IGNORE INTO jobs
                (id, title, PositionURI, company, location, category, career_level,
                 start_date, description, requirements, fetched_at, score, eval_option, reason, PublicationStartDate, PublicationEndDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.conn.execute(
                insert_sql,
                (
                    job["id"],
                    job["title"],
                    job["PositionURI"],
                    job["company"],
                    job["location"],
                    job["category"],
                    job["career_level"],
                    job["start_date"],
                    job["description"],
                    job["requirements"],
                    datetime.utcnow().isoformat(),
                    -1,
                    "Base",
                    "",
                    job["PublicationStartDate"],
                    job["PublicationEndDate"],
                ),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Insert failed for job {job.get('id', 'unknown')}: {e}")

    def fetch_all(self):
        """Fetch all jobs from database"""
        try:
            cur = self.conn.execute("SELECT * FROM jobs ORDER BY fetched_at DESC")
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Fetch all failed: {e}")
            return []

    def fetch_new(self, since):
        """Fetch jobs newer than given timestamp"""
        try:
            cur = self.conn.execute(
                "SELECT * FROM jobs WHERE fetched_at > ? ORDER BY fetched_at DESC",
                (since,),
            )
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Fetch new failed: {e}")
            return []

    def get_count(self):
        """Get total number of jobs"""
        try:
            cur = self.conn.execute("SELECT COUNT(*) FROM jobs")
            return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0

    def edit_job(self, job_id, key, value):
        """
        Update the value of a specific job field.

        args:
            job_id: The ID of the job to update.
            key: The field to update (e.g., 'title', 'company').
            value: The new value for the field.
        """
        try:
            update_sql = f"UPDATE jobs SET {key} = ? WHERE id = ?"
            self.conn.execute(update_sql, (value, job_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Update failed for job {job_id}: {e}")

    @property
    def table_df(self) -> pd.DataFrame:
        """Get jobs table as DataFrame"""
        jobs = self.fetch_all()

        return pd.DataFrame(jobs) if jobs else pd.DataFrame(columns=self.job_columns)

    @property
    def all_ids(self):
        """Get all job IDs in the database"""
        try:
            cur = self.conn.execute("SELECT id FROM jobs")
            return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Fetch all IDs failed: {e}")
            return []

    @property
    def all_jobs(self):
        """Get all jobs in the database"""
        try:
            cur = self.conn.execute("SELECT * FROM jobs")
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Fetch all jobs failed: {e}")
            return []
