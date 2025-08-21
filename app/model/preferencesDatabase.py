import sqlite3

from app.logger import logger
from app.config import DB_PATH


class PreferencesDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to settings database: {self.db_path}")
        except Exception as e:
            logger.error(f"Settings database connection failed: {e}")
            raise

    def _create_table(self):
        """Create settings table if it doesn't exist"""
        try:
            create_sql = """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """
            self.conn.execute(create_sql)
            self.conn.commit()
            logger.info("Settings table created or already exists.")
        except Exception as e:
            logger.error(f"Settings table creation failed: {e}")
            raise

    def set(self, key, value):
        """Set a setting value"""
        try:
            insert_sql = """
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """
            self.conn.execute(insert_sql, (key, value))
            self.conn.commit()
            logger.info(f"Setting updated: {key}")
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")

    def get(self, key):
        """Get a setting value"""
        try:
            cur = self.conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            return None