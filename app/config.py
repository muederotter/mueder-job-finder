"""
This module is used to manage the configuration settings for the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Default database file
DB_PATH = "muederjobfinder.db"

# Job API URL
JOB_API_LINK = os.getenv("JOB_API_LINK", "")

# Request origin
REQUEST_ORIGIN = os.getenv("REQUEST_ORIGIN", "")

# OpenAI API key storage
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")